from unittest.mock import MagicMock, call, patch

import pytest
import pandas as pd
from nrdtech_aws_utils.firehose_helper import FirehoseHelper


def test_send_records_to_firehose_success():
    firehose_client = MagicMock()
    firehose_client.put_record_batch = MagicMock(return_value={"FailedPutCount": 0})
    with FirehoseHelper(firehose_client, "deliveryStreamName") as firehose_helper:
        firehose_helper.send_records_to_firehose([b"test", b"test2"])
        firehose_client.put_record_batch.assert_called_once_with(
            DeliveryStreamName="deliveryStreamName",
            Records=[{"Data": b"test\n"}, {"Data": b"test2\n"}],
        )


def test_send_records_to_firehose_success2():
    firehose_client = MagicMock()
    firehose_client.put_record_batch = MagicMock(return_value={"FailedPutCount": 0})
    firehose_client.close = MagicMock()
    with FirehoseHelper(firehose_client, "deliveryStreamName") as firehose_helper:
        firehose_helper.send_records_to_firehose(
            [b"0", b"1", b"2", b"3", b"4", "5", "6", "7", "8", "9", "00"]
        )
        calls = [
            call(
                DeliveryStreamName="deliveryStreamName",
                Records=[
                    {"Data": b"0\n"},
                    {"Data": b"1\n"},
                    {"Data": b"2\n"},
                    {"Data": b"3\n"},
                    {"Data": b"4\n"},
                    {"Data": b"5\n"},
                    {"Data": b"6\n"},
                    {"Data": b"7\n"},
                    {"Data": b"8\n"},
                    {"Data": b"9\n"},
                ],
            ),
            call(
                DeliveryStreamName="deliveryStreamName",
                Records=[{"Data": b"00\n"}],
            ),
        ]
        firehose_client.put_record_batch.assert_has_calls(calls)
    firehose_client.close.assert_called_once()


def test_send_records_to_firehose_failure():
    firehose_client = MagicMock()
    firehose_client.put_record_batch = MagicMock(return_value={"FailedPutCount": 1})
    firehose_helper = FirehoseHelper(firehose_client, "deliveryStreamName")
    with pytest.raises(Exception):
        firehose_helper.send_records_to_firehose(["test", "test2"])


def convert_df_to_firehose_records():
    df = MagicMock()
    df.to_csv = MagicMock(return_value="test\ntest2\n")
    records = FirehoseHelper.convert_df_to_firehose_records(df)
    assert records == [{"Data": b"test\ntest2\n"}]


def convert_df_to_firehose_records_failure():
    df = MagicMock()
    df.to_csv = MagicMock(return_value="test\ntest2\n")
    with pytest.raises(Exception):
        FirehoseHelper.convert_df_to_firehose_records(df)


def test_send_df_to_firehose_success():
    firehose_client = MagicMock()
    firehose_client.put_record_batch = MagicMock(return_value={"FailedPutCount": 0})
    with FirehoseHelper(firehose_client, "deliveryStreamName") as firehose_helper:
        df = pd.DataFrame(
            [{"test1": "test2", "test_num": 3}, {"test_str": "test", "test_num": 5}]
        )
        firehose_helper.send_df_to_firehose(df)
        firehose_client.put_record_batch.assert_called_once_with(
            DeliveryStreamName="deliveryStreamName",
            Records=[{"Data": b"test2,3,\\N\n\\N,5,test\n"}],
        )


def test_send_df_to_firehose_failure():
    firehose_client = MagicMock()
    firehose_client.put_record_batch = MagicMock(return_value={"FailedPutCount": 1})
    firehose_helper = FirehoseHelper(firehose_client, "deliveryStreamName")
    df = pd.DataFrame(
        [{"test1": "test2", "test_num": 3}, {"test_str": "test", "test_num": 5}]
    )
    with pytest.raises(Exception):
        firehose_helper.send_df_to_firehose(df)


def test_send_df_to_firehose_records_none():
    firehose_client = MagicMock()
    firehose_helper = FirehoseHelper(firehose_client, "deliveryStreamName")
    df = MagicMock()
    with patch.object(
        FirehoseHelper, "_convert_df_to_firehose_records", return_value=None
    ):
        with pytest.raises(Exception, match="Failed to send records to firehose"):
            firehose_helper.send_df_to_firehose(df)
