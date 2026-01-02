from datetime import datetime
import os
from itertools import islice
from typing import Any, Iterator, Optional

from boto3.dynamodb.conditions import Key, ConditionBase
from boto3.dynamodb.types import TypeDeserializer


class DynamodbTable:
    def __init__(
        self,
        dynamodb_resource,
        table: str,
        primary_key: str = "id",
        secondary_key: str = "sub_id",
        automatically_append_env_to_table_name=False,
    ):
        self._dynamodb_resource = dynamodb_resource
        self._automatically_append_env_to_table_name = (
            automatically_append_env_to_table_name
        )
        self._table = self._dynamodb_resource.Table(self._get_full_table_name(table))
        self._primary_key = primary_key
        self._secondary_key = secondary_key

    def _get_full_table_name(self, table_name: str):
        if self._automatically_append_env_to_table_name:
            return f"{table_name}-{os.environ['ENVIRONMENT']}"
        return table_name

    def put_item(self, item: dict):
        item_converted = self._convert_datetime_to_string(item)
        self._table.put_item(Item=item_converted)

    @staticmethod
    def _convert_datetime_to_string(item):
        """
        Recursively convert all datetime objects in a dictionary to ISO 8601 formatted strings.
        """
        if isinstance(item, dict):
            return {
                k: DynamodbTable._convert_datetime_to_string(v) for k, v in item.items()
            }
        elif isinstance(item, list):
            return [DynamodbTable._convert_datetime_to_string(v) for v in item]
        elif isinstance(item, datetime):
            return item.isoformat()
        else:
            return item

    def put_items(self, items: list):
        chunk_size = 25
        it = iter(items)

        while True:
            chunk = list(islice(it, chunk_size))
            if not chunk:
                break

            with self._table.batch_writer() as batch:
                for item in chunk:
                    item_converted = self._convert_datetime_to_string(item)
                    batch.put_item(Item=item_converted)

    def get_item_with_id_and_sub_id(self, id, sub_id) -> dict | None:
        response = self._table.query(
            KeyConditionExpression=Key(self._primary_key).eq(id)
            & Key(self._secondary_key).eq(sub_id)
        )
        items = response.get("Items", [])
        return items[0] if items else None

    def get_items_with_id_and_sub_id_prefix(self, id, sub_id_prefix: str) -> list:
        response = self._table.query(
            KeyConditionExpression=Key(self._primary_key).eq(id)
            & Key(self._secondary_key).begins_with(sub_id_prefix)
        )
        return response.get("Items", [])

    def get_items_with_id(self, id, index_name: Optional[str] = None) -> list:
        if index_name:
            response = self._table.query(
                IndexName=index_name,
                KeyConditionExpression=Key(self._primary_key).eq(id),
            )
        else:
            response = self._table.query(
                KeyConditionExpression=Key(self._primary_key).eq(id)
            )
        return response.get("Items", [])

    def increment_counter(self, id, sub_id, counter_name: str, increment: int = 1):
        # Atomically increment the counter
        response = self._table.update_item(
            Key={self._primary_key: id, self._secondary_key: sub_id},
            UpdateExpression=f"ADD {counter_name} :inc",
            ExpressionAttributeValues={":inc": increment},
            ReturnValues="UPDATED_NEW",
        )
        return response["Attributes"][counter_name]

    def delete_item(self, id: str, sort_key=None):
        key = {self._primary_key: id}
        if self._secondary_key and sort_key is not None:
            key[self._secondary_key] = sort_key
        self._table.delete_item(Key=key)

    def scan(self, filter_expression: ConditionBase) -> Iterator[dict[str, Any]]:
        response = self._table.scan(FilterExpression=filter_expression)

        for item in response.get("Items", []):
            yield item

        while "LastEvaluatedKey" in response:
            response = self._table.scan(
                FilterExpression=filter_expression,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )

            for item in response.get("Items", []):
                yield item

    class _BatchWriter:
        def __init__(self, table, primary_key: str, sort_key=None):
            self.table = table
            self.batch_writer = table.batch_writer()
            self.primary_key = primary_key
            self.sort_key = sort_key

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Ensure the batch_writer's __exit__ is called to flush the batch
            self.batch_writer.__exit__(exc_type, exc_val, exc_tb)

        def delete_item(self, pk_value, sk_value=None):
            key = {self.primary_key: pk_value}
            if self.sort_key and sk_value is not None:
                key[self.sort_key] = sk_value
            self.batch_writer.delete_item(Key=key)

        def put_item(self, item):
            self.batch_writer.put_item(Item=item)

    def get_batch_writer(self):
        return DynamodbTable._BatchWriter(
            self._table,
            self._primary_key,
            self._secondary_key,
        )


def deserialize_dynamodb_image(image: dict) -> dict | None:
    if image is None:
        return None
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in image.items()}
