#!/usr/local/bin/python3

from aws_handler import S3, SQS
import cv2
import argparse
import os.path as op


def sqs_worker(s3, sqs, batch_size=1):
    response = sqs.receive(batch_size)
    print(response)
    if not response.get('Messages'):
        print("Message not found!")
        return
    messages = response['Messages']
    for msg in messages:
        s3_dir = msg['Body']
        filename = op.basename(s3_dir)
        s3.download(s3_dir, filename)
        img = cv2.imread(filename)
        img = cv2.resize(img, (64, 64))
        cv2.imwrite(filename, img)
        s3.upload(filename, s3_dir)
    sqs.delete(len(messages))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch_size', type=int, default=1)
    args = parser.parse_args()
    batch_size = args.batch_size
    s3 = S3.sample()
    sqs = SQS.sample()
    sqs_worker(s3, sqs, batch_size)

