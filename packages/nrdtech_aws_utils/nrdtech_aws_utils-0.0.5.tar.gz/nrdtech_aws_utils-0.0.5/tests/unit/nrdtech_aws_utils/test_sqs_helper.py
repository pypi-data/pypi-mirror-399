from unittest.mock import MagicMock, ANY, call

import pytest

from nrdtech_aws_utils.sqs_helper import Message, SqsHelper, SqsMessageSendFailure


def test_send_message_non_fifo_success():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with SqsHelper(sqs_client, "test_sqs_url", initial_backoff_time=0) as sqs:
        for i in range(3):
            sqs.send_message(Message("hello world"))
    sqs_client.send_message_batch.assert_called_with(
        QueueUrl="test_sqs_url",
        Entries=[
            {"Id": ANY, "MessageBody": "hello world"},
        ],
    )


def test_send_message_non_fifo_failure():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock(
        return_value={"Failed": "some error message"}
    )
    sqs_client.close = MagicMock()
    with pytest.raises(SqsMessageSendFailure) as err:
        with SqsHelper(sqs_client, "test_sqs_url", initial_backoff_time=0) as sqs:
            for i in range(3):
                sqs.send_message(Message("hello world"))
        assert "some error message" in str(err.value)


def test_send_message_non_fifo_allow_dups_success():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with SqsHelper(
        sqs_client, "test_sqs_url", deduplicate=False, initial_backoff_time=0
    ) as sqs:
        for i in range(3):
            sqs.send_message(Message("hello world"))
    sqs_client.send_message_batch.assert_called_with(
        QueueUrl="test_sqs_url",
        Entries=[
            {"Id": ANY, "MessageBody": "hello world"},
            {"Id": ANY, "MessageBody": "hello world"},
            {"Id": ANY, "MessageBody": "hello world"},
        ],
    )


def test_send_message_non_fifo_allow_dups_with_delay_success():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with SqsHelper(
        sqs_client, "test_sqs_url", deduplicate=False, initial_backoff_time=0
    ) as sqs:
        for i in range(3):
            sqs.send_message(Message("hello world", delay_seconds=5))
    sqs_client.send_message_batch.assert_called_with(
        QueueUrl="test_sqs_url",
        Entries=[
            {"Id": ANY, "MessageBody": "hello world", "DelaySeconds": 5},
            {"Id": ANY, "MessageBody": "hello world", "DelaySeconds": 5},
            {"Id": ANY, "MessageBody": "hello world", "DelaySeconds": 5},
        ],
    )


def test_send_message_non_fifo_allow_dups_two_batches_success():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with SqsHelper(
        sqs_client, "test_sqs_url", deduplicate=False, initial_backoff_time=0
    ) as sqs:
        for i in range(15):
            sqs.send_message(Message("hello world"))
    calls = [
        call(
            QueueUrl="test_sqs_url",
            Entries=[
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
            ],
        ),
        call(
            QueueUrl="test_sqs_url",
            Entries=[
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
                {"Id": ANY, "MessageBody": "hello world"},
            ],
        ),
    ]
    sqs_client.send_message_batch.assert_has_calls(calls, any_order=True)


def test_send_message_fifo_missing_message_group_id():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with pytest.raises(AssertionError) as err:
        with SqsHelper(sqs_client, "test_sqs_url.fifo", initial_backoff_time=0) as sqs:
            for i in range(3):
                sqs.send_message(Message("hello world"))
        assert "message_group_id cannot be null" in str(err.value)


def test_send_message_fifo_invalid_delay_messages():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with pytest.raises(AssertionError) as err:
        with SqsHelper(sqs_client, "test_sqs_url.fifo", initial_backoff_time=0) as sqs:
            for i in range(3):
                sqs.send_message(
                    Message(
                        "hello world", message_group_id="test_group", delay_seconds=5
                    )
                )
        assert "delay_seconds cannot be set" in str(err.value)


def test_send_message_fifo_success():
    sqs_client = MagicMock()
    sqs_client.send_message_batch = MagicMock()
    sqs_client.close = MagicMock()
    with SqsHelper(sqs_client, "test_sqs_url.fifo", initial_backoff_time=0) as sqs:
        for i in range(3):
            sqs.send_message(Message("hello world", message_group_id="test_group"))
    sqs_client.send_message_batch.assert_called_with(
        QueueUrl="test_sqs_url.fifo",
        Entries=[
            {"Id": ANY, "MessageBody": "hello world", "MessageGroupId": "test_group"},
        ],
    )
