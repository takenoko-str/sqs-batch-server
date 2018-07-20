#!/usr/local/bin/python3

import os
import boto3
import os.path as op
from datetime import date


class S3:
    BUCKET = os.environ.get('S3_BUCKET')

    def __init__(self, bucket):
        self.client = boto3.client('s3', region_name='ap-northeast-1')
        self.bucket = bucket

    @classmethod
    def sample(cls):
        return cls(cls.BUCKET)

    def upload(self, src_file_path, dst_file_path):
        self.client.upload_file(src_file_path, self.bucket, dst_file_path)

    def download(self, src_file_path, dst_file_path):
        return self.client.download_file(self.bucket, src_file_path, dst_file_path)

    def put(self, key, body):
        self.client.put_object(Body=body, Bucket=self.bucket, Key=key)

    def get(self, key):
        return self.client.get_object(Bucket=self.bucket, Key=key)['Body'].read()

    @classmethod
    def create_folder_with_timestamp(cls, path):
        today = str(date.today())
        return op.join(today, path)


def s3_example(key):
    x = S3.sample()
    y = x.get(key)
    print(y['Body'].read().decode('utf-8'))