import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from boto3.dynamodb.conditions import Key

from nrdtech_aws_utils.dynamodb_table import (
    deserialize_dynamodb_image,
    DynamodbTable,
)


# Mocking AWS DynamoDB
@pytest.fixture
def mock_dynamodb_resource():
    with patch("boto3.resource") as mock_resource:
        mock_table = MagicMock()
        mock_resource.Table.return_value = mock_table
        yield mock_resource, mock_table


@pytest.fixture
def dynamodb_table(mock_dynamodb_resource):
    mock_resource, _ = mock_dynamodb_resource
    os.environ["ENVIRONMENT"] = "test"
    return DynamodbTable(mock_resource, "test_table")


@pytest.fixture
def dynamodb_table_env_mod(mock_dynamodb_resource):
    mock_resource, _ = mock_dynamodb_resource
    os.environ["ENVIRONMENT"] = "test"
    return DynamodbTable(
        mock_resource, "test_table", automatically_append_env_to_table_name=True
    )


class TestDynamodbTable:
    def test_init(self, dynamodb_table):
        assert dynamodb_table._primary_key == "id"
        assert dynamodb_table._secondary_key == "sub_id"

    def test_get_full_table_name(self, dynamodb_table, dynamodb_table_env_mod):
        assert dynamodb_table._get_full_table_name("my_table") == "my_table"
        assert (
            dynamodb_table_env_mod._get_full_table_name("my_table") == "my_table-test"
        )

    def test_put_item(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        item = {"id": "123", "data": "test"}
        dynamodb_table.put_item(item)
        mock_table.put_item.assert_called_with(Item=item)

    def test_put_items(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        items = [{"id": str(i), "data": "test"} for i in range(30)]
        dynamodb_table.put_items(items)
        assert mock_table.batch_writer.call_count == 2  # Assuming 25 items per batch

    def test_get_item_with_id_and_sub_id(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_table.query.return_value = {"Items": [{"id": "123", "sub_id": "456"}]}
        result = dynamodb_table.get_item_with_id_and_sub_id("123", "456")
        assert result == {"id": "123", "sub_id": "456"}

    def test_get_items_with_id_and_sub_id_prefix(
        self, dynamodb_table, mock_dynamodb_resource
    ):
        _, mock_table = mock_dynamodb_resource
        mock_table.query.return_value = {"Items": [{"id": "123", "sub_id": "45"}]}
        result = dynamodb_table.get_items_with_id_and_sub_id_prefix("123", "45")
        assert result == [{"id": "123", "sub_id": "45"}]

    def test_get_items_with_id(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_table.query.return_value = {"Items": [{"id": "123"}]}
        result = dynamodb_table.get_items_with_id("123")
        assert result == [{"id": "123"}]

    def test_get_items_with_id_with_index(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_table.query.return_value = {"Items": [{"id": "123", "sub_id": "456"}]}
        result = dynamodb_table.get_items_with_id("123", index_name="test-index")
        assert result == [{"id": "123", "sub_id": "456"}]
        mock_table.query.assert_called_with(
            IndexName="test-index",
            KeyConditionExpression=Key("id").eq("123"),
        )

    def test_put_item_with_datetime(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        now = datetime.now()
        item = {"id": "123", "data": "test", "timestamp": now}
        dynamodb_table.put_item(item)
        expected_item = {"id": "123", "data": "test", "timestamp": now.isoformat()}
        mock_table.put_item.assert_called_with(Item=expected_item)

    def test_put_item_with_nested_datetime(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        now = datetime.now()
        item = {
            "id": "123",
            "data": {"nested": {"timestamp": now}},
            "list": [now, "string", {"another": now}],
        }
        dynamodb_table.put_item(item)
        expected_item = {
            "id": "123",
            "data": {"nested": {"timestamp": now.isoformat()}},
            "list": [now.isoformat(), "string", {"another": now.isoformat()}],
        }
        mock_table.put_item.assert_called_with(Item=expected_item)

    def test_put_items_with_datetime(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        now = datetime.now()
        items = [{"id": str(i), "timestamp": now} for i in range(5)]
        dynamodb_table.put_items(items)
        assert mock_table.batch_writer.call_count == 1

    def test_increment_counter(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_table.update_item.return_value = {"Attributes": {"counter": 5}}
        result = dynamodb_table.increment_counter("123", "456", "counter", increment=1)
        assert result == 5
        mock_table.update_item.assert_called_with(
            Key={"id": "123", "sub_id": "456"},
            UpdateExpression="ADD counter :inc",
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW",
        )

    def test_increment_counter_custom_increment(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_table.update_item.return_value = {"Attributes": {"counter": 10}}
        result = dynamodb_table.increment_counter("123", "456", "counter", increment=5)
        assert result == 10
        mock_table.update_item.assert_called_with(
            Key={"id": "123", "sub_id": "456"},
            UpdateExpression="ADD counter :inc",
            ExpressionAttributeValues={":inc": 5},
            ReturnValues="UPDATED_NEW",
        )

    def test_delete_item_with_sort_key(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        dynamodb_table.delete_item("123", sort_key="456")
        mock_table.delete_item.assert_called_with(Key={"id": "123", "sub_id": "456"})

    def test_delete_item_without_sort_key(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        dynamodb_table.delete_item("123")
        mock_table.delete_item.assert_called_with(Key={"id": "123"})

    def test_scan_with_filter(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        filter_expr = Key("id").eq("123")
        mock_table.scan.return_value = {"Items": [{"id": "123", "data": "test"}]}
        results = list(dynamodb_table.scan(filter_expr))
        assert results == [{"id": "123", "data": "test"}]
        mock_table.scan.assert_called_with(FilterExpression=filter_expr)

    def test_scan_with_pagination(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        filter_expr = Key("id").eq("123")
        mock_table.scan.side_effect = [
            {
                "Items": [{"id": "123", "data": "test1"}],
                "LastEvaluatedKey": {"id": "123"},
            },
            {"Items": [{"id": "123", "data": "test2"}]},
        ]
        results = list(dynamodb_table.scan(filter_expr))
        assert results == [
            {"id": "123", "data": "test1"},
            {"id": "123", "data": "test2"},
        ]
        assert mock_table.scan.call_count == 2
        mock_table.scan.assert_called_with(
            FilterExpression=filter_expr,
            ExclusiveStartKey={"id": "123"},
        )

    def test_get_batch_writer(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value = mock_batch_writer
        batch_writer = dynamodb_table.get_batch_writer()
        assert batch_writer.primary_key == "id"
        assert batch_writer.sort_key == "sub_id"

    def test_batch_writer_put_item(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value = mock_batch_writer
        batch_writer = dynamodb_table.get_batch_writer()
        item = {"id": "123", "sub_id": "456", "data": "test"}
        batch_writer.put_item(item)
        mock_batch_writer.put_item.assert_called_with(Item=item)

    def test_batch_writer_delete_item_with_sort_key(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value = mock_batch_writer
        batch_writer = dynamodb_table.get_batch_writer()
        batch_writer.delete_item("123", "456")
        mock_batch_writer.delete_item.assert_called_with(Key={"id": "123", "sub_id": "456"})

    def test_batch_writer_delete_item_without_sort_key(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value = mock_batch_writer
        batch_writer = dynamodb_table.get_batch_writer()
        batch_writer.delete_item("123")
        mock_batch_writer.delete_item.assert_called_with(Key={"id": "123"})

    def test_batch_writer_context_manager(self, dynamodb_table, mock_dynamodb_resource):
        _, mock_table = mock_dynamodb_resource
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value = mock_batch_writer
        with dynamodb_table.get_batch_writer() as batch_writer:
            batch_writer.put_item({"id": "123", "data": "test"})
        # Verify __exit__ was called on the underlying batch_writer
        mock_batch_writer.__exit__.assert_called_once()


def test_deserialize_dynamodb_image():
    image = {"key": {"S": "value"}}
    assert deserialize_dynamodb_image(image) == {"key": "value"}

    assert deserialize_dynamodb_image(None) is None
