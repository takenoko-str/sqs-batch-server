#!/usr/local/bin/python3

import os
import os.path as op
import sys
import boto3
import random
import argparse
from settings import *


class SQS:
    SQS_URL = os.environ.get('SQS_URL')

    def __init__(self, url):
        self.url = url
        self.sqs = boto3.client('sqs', region_name='ap-northeast-1')
        self.messages = []

    @classmethod
    def sample(cls):
        return cls(cls.SQS_URL)

    def send(self, body_message):
        self.sqs.send_message(QueueUrl=self.url, MessageBody=body_message)

    def receive(self, num_messages=1):
        message = self.sqs.receive_message(QueueUrl=self.url, MaxNumberOfMessages=num_messages)
        self.messages.append(message)
        return message

    def delete(self, num_messages=1):
        i = 0
        while i < num_messages:
            if self.messages == []:
                break
            msg = self.messages.pop(0)
            if msg.get('Messages'):
                for q in msg['Messages']:
                    self.sqs.delete_message(QueueUrl=self.url, ReceiptHandle=q['ReceiptHandle'])
            else:
                print("Queue is now empty")
            i += 1


class S3:
    S3_BUCKET = os.environ.get('S3_BUCKET')

    def __init__(self, s3_bucket):
        self.s3 = boto3.client('s3', region_name='ap-northeast-1')
        self.s3_bucket = s3_bucket

    @classmethod
    def sample(cls):
        return cls(cls.S3_BUCKET)

    def upload(self, src_file_path, dst_file_path):
        self.s3.upload_file(src_file_path, self.s3_bucket, dst_file_path)

    def download(self, src_file_path, dst_file_path):
        return self.s3.download_file(self.s3_bucket, src_file_path, dst_file_path)

    def put(self, key, body):
        self.s3.put_object(Body=body, Bucket=self.s3_bucket, Key=key)

    def get(self, key):
        return self.s3.get_object(Bucket=self.s3_bucket, Key=key)['Body'].read()


def s3_example(key):
    x = S3.sample()
    y = x.get(key)
    print(y['Body'].read().decode('utf-8'))


def sqs_example():
    x = SQS.sample()
    y = []
    for i in range(3):
        y.append(x.receive(10))
    print(y)


def main():
    # s3_example("hoge")
    sqs_example()


if __name__ == '__main__':
    main()

