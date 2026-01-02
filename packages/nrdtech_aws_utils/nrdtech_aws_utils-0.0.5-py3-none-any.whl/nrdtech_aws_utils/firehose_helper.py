import json
import pandas as pd

from nrdtech_utils.list_helper import chunk_list

DEFAULT_MAX_FIREHOSE_BATCH_SIZE = 10


class FirehoseHelper:
    def __init__(
        self,
        firehose_client,
        delivery_stream_name,
        max_firehose_batch_size=DEFAULT_MAX_FIREHOSE_BATCH_SIZE,
    ):
        self._firehose_client = firehose_client
        self._delivery_stream_name = delivery_stream_name
        self._max_firehose_batch_size = max_firehose_batch_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._firehose_client.close()

    def send_records_to_firehose(self, records: list):
        chunked_records = chunk_list(records, self._max_firehose_batch_size)
        for record_chunk in chunked_records:
            self._send_formatted_record_to_firehose(record_chunk)

    def _send_formatted_record_to_firehose(self, record_chunk: list):
        firehose_records = FirehoseHelper._format_firehose_records(record_chunk)
        response = self._firehose_client.put_record_batch(
            DeliveryStreamName=self._delivery_stream_name, Records=firehose_records
        )
        if response is None or response["FailedPutCount"] > 0:
            raise Exception(
                f"Failed to send records to firehose: {json.dumps(response)}"
            )

    def send_df_to_firehose(self, df):
        records = self._convert_df_to_firehose_records(df)
        if records is None:
            raise Exception(f"Failed to send records to firehose")
        self.send_records_to_firehose(records)
        return True

    @staticmethod
    def _convert_df_to_firehose_records(df):
        encoded_values = bytes(
            df.to_csv(header=False, lineterminator="\n", index=False, na_rep="\\N"),
            encoding="utf-8",
        )
        records = [encoded_values]
        return records

    @staticmethod
    def _format_firehose_records(list_of_strings: list):
        return [FirehoseHelper._format_firehose_record(x) for x in list_of_strings]

    @staticmethod
    def _format_firehose_record(input_string):
        if type(input_string) != bytes:
            input_string = bytes(input_string, "utf-8")
        if not input_string.endswith(b"\n"):
            input_string += b"\n"
        return {"Data": input_string}
