#!/usr/local/bin/python3

from aws_handler import S3, SQS
import os.path as op
import argparse


def sqs_client(s3, sqs, path, bucket_path='img'):
    filename = op.basename(path)
    s3_dir = op.join(bucket_path, filename)
    try:
        s3.upload(file_path, s3_dir)
        sqs.send(s3_dir)
        print(sqs.receive())
    except:
        print("Upload failed")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--s3_dir', default='img')
    args = parser.parse_args()
    file_path = args.s3_dir
    s3 = S3.sample()
    sqs = SQS.sample()
    sqs_client(s3, sqs, file_path)

