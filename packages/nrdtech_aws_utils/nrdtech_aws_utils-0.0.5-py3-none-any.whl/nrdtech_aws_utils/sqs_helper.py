import hashlib
import json
import time
import traceback
from typing import List


class Message:
    def __init__(
        self, body, delay_seconds=None, message_id=None, message_group_id=None
    ):
        self.body = body
        self.delay_seconds = delay_seconds
        self.message_id = (
            message_id
            if message_id is not None
            else hashlib.md5(bytes(body, "utf-8")).hexdigest()
        )
        self.message_group_id = message_group_id


class SqsHelper:
    def __init__(
        self,
        sqs_client,
        queue: str,
        deduplicate=True,
        max_retries=5,
        initial_backoff_time=1,
    ):
        self.sqs_client = sqs_client
        self.queue = queue
        self.deduplicate = deduplicate
        self.message_buffer = []
        self.max_retries = max_retries
        self.initial_backoff_time = initial_backoff_time

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__flush_batched_messages_to_sqs()
        self.sqs_client.close()

    def send_message(self, message: Message):
        self.message_buffer.append(message)
        if len(self.message_buffer) >= 10:
            self.__flush_batched_messages_to_sqs()

    def send_messages(self, messages: List[Message]):
        backoff_time = self.initial_backoff_time
        for attempt in range(self.max_retries):
            try:
                prepared_messages = [
                    self.__create_sqs_entry_for_obj(m)
                    for m in self.__prepare_messages_to_send(messages)
                ]
                result = self.sqs_client.send_message_batch(
                    QueueUrl=self.queue,
                    Entries=prepared_messages,
                )

                if "Failed" in result and len(result["Failed"]) > 0:
                    raise SqsMessageSendFailure(json.dumps(result["Failed"]))
                return  # Exit the method if successful

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Exponentially increase the backoff time
                else:
                    raise e  # Re-raise the last exception after all retries

    def __prepare_messages_to_send(self, messages):
        if self.deduplicate:
            return self.__deduplicate_messages(messages)
        return messages

    @staticmethod
    def __deduplicate_messages(messages: list[Message]):
        tmp = set()
        unique_messages = []
        for m in messages:
            if m.message_id not in tmp:
                unique_messages.append(m)
                tmp.add(m.message_id)
        return unique_messages

    def __flush_batched_messages_to_sqs(self):
        if len(self.message_buffer) > 0:
            self.send_messages(self.message_buffer)
            self.__reset_message_buffer()

    def __create_sqs_entry_for_obj(self, message: Message):
        sqs_message = {"Id": message.message_id, "MessageBody": message.body}
        if self.queue.endswith(".fifo"):
            assert (
                message.message_group_id is not None
            ), "message_group_id cannot be null for fifo queue messages"
            assert (
                message.delay_seconds is None
            ), "delay_seconds cannot be set on fifo queue messages because it is not supported"
            sqs_message["MessageGroupId"] = message.message_group_id
        else:
            if message.delay_seconds is not None and message.delay_seconds > 0:
                sqs_message["DelaySeconds"] = message.delay_seconds
        return sqs_message

    def __reset_message_buffer(self):
        self.message_buffer = []


class SqsMessageSendFailure(Exception):
    pass
