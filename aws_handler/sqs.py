#!/usr/local/bin/python3

import os
import boto3


class SQS:
    URL = os.environ.get('SQS_URL')
    MAX_QUEUE_SIZE = 10

    def __init__(self, url):
        self.url = url
        self.client = boto3.client('sqs', region_name='ap-northeast-1')
        self.messages = []

    @classmethod
    def sample(cls):
        return cls(cls.URL)

    def send(self, body_message):
        self.client.send_message(QueueUrl=self.url, MessageBody=body_message)

    def receive(self, num_messages=1):
        num_messages = num_messages % self.MAX_QUEUE_SIZE + 1
        response = self.client.receive_message(QueueUrl=self.url, MaxNumberOfMessages=num_messages)
        messages = response.get('Messages')
        if messages:
            self.messages += messages
        return messages

    def delete(self, messages):
        for msg in messages:
            self.client.delete_message(QueueUrl=self.url, ReceiptHandle=msg['ReceiptHandle'])

    def message_size(self):
        response = self.client.get_queue_attributes(
            QueueUrl=self.url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        attr = response.get('Attributes')
        if attr is not None:
            msg = attr['ApproximateNumberOfMessages']
        else:
            msg = '0'
        return msg


def sqs_example():
    sqs = SQS.sample()
    print(sqs.create_queue("test3"))
    # y = []
    # for i in range(3):
    #     y.append(sqs.receive(10))
    # print(y)
