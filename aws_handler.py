#!/usr/local/bin/python3

import os
import os.path as op
import cv2
import sys
import boto3
import random
import argparse
from setting import *


class SQS:
    SQS_URL = os.environ['SQS_URL']

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
            msg = self.messages.pop(0)
            if msg.get('Messages'):
                self.sqs.delete_message(QueueUrl=self.url, ReceiptHandle=msg['Messages'][0]['ReceiptHandle'])
            else:
                print("Queue is now empty")
            i += 1


class S3:
    S3_BUCKET = os.environ['S3_BUCKET']

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

