#!/usr/local/bin/python3

import os
import boto3
import settings


class SQS:
    URL = os.environ.get('SQS_URL')

    def __init__(self, url):
        self.url = url
        self.sqs = boto3.client('sqs', region_name='ap-northeast-1')
        self.messages = []

    @classmethod
    def sample(cls):
        return cls(cls.URL)

    def send(self, body_message):
        self.sqs.send_message(QueueUrl=self.url, MessageBody=body_message)

    def receive(self, num_messages=1):
        num_messages = num_messages % (settings.MAX_QUEUE_SIZE + 1)
        response = self.sqs.receive_message(QueueUrl=self.url, MaxNumberOfMessages=num_messages)
        messages = response.get('Messages')
        if messages:
            self.messages += messages
        return messages

    def delete(self, messages):
        for msg in messages:
            self.sqs.delete_message(QueueUrl=self.url, ReceiptHandle=msg['ReceiptHandle'])

    def message_size(self):
        response = self.sqs.get_queue_attributes(
            QueueUrl=self.url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        attr = response.get('Attributes')
        if attr is not None:
            msg = attr['ApproximateNumberOfMessages']
        else:
            msg = '0'
        return msg


class S3:
    BUCKET = os.environ.get('S3_BUCKET')

    def __init__(self, bucket):
        self.s3 = boto3.client('s3', region_name='ap-northeast-1')
        self.bucket = bucket

    @classmethod
    def sample(cls):
        return cls(cls.BUCKET)

    def upload(self, src_file_path, dst_file_path):
        self.s3.upload_file(src_file_path, self.bucket, dst_file_path)

    def download(self, src_file_path, dst_file_path):
        return self.s3.download_file(self.bucket, src_file_path, dst_file_path)

    def put(self, key, body):
        self.s3.put_object(Body=body, Bucket=self.bucket, Key=key)

    def get(self, key):
        return self.s3.get_object(Bucket=self.bucket, Key=key)['Body'].read()


class EC2:
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')

    def __init__(self, ids):
        self.ids = ids

    @classmethod
    def describe(cls, filters, ids=[]):
        response = cls.ec2.describe_instances(Filters=filters)
        for reservation in response.get('Reservations', [{}]):
            for instance in reservation.get('Instances', [{}]):
                ids.append(instance.get('InstanceId'))
        return cls(ids)

    def start(self):
        self.ec2.start_instances(InstanceIds=self.ids)

    def stop(self):
        self.ec2.stop_instances(InstanceIds=self.ids)


class SNS:
    TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

    def __init__(self, topic_arn):
        self.client = boto3.client('sns', region_name='ap-northeast-1')
        self.topic_arn = topic_arn

    @classmethod
    def sample(cls):
        return cls(cls.TOPIC_ARN)

    def set_subscription(self, subscription_arn, model_name):
        self.client.set_subscription_attributes(
            SubscriptionArn=subscription_arn,
            AttributeName='FilterPolicy',
            AttributeValue='{"model": ["' + model_name + '"]}'
        )

    def publish(self, message, model_name):
        subject = 'Test #1234'
        message_attributes = {'model': {
                                  'DataType': 'String',
                                  'StringValue': model_name}
                              }
        self.client.publish(TopicArn=self.topic_arn,
                            Subject=subject,
                            Message=message,
                            MessageAttributes=message_attributes
                            )


def s3_example(key):
    x = S3.sample()
    y = x.get(key)
    print(y['Body'].read().decode('utf-8'))


def sqs_example():
    sqs = SQS.sample()
    y = []
    for i in range(3):
        y.append(sqs.receive(10))
    print(y)


def sns_example():
    sns = SNS.sample()
    sns.publish('Male, 33 years old', 'test')


def main():
    # s3_example("hoge")
    # sqs_example()
    sns_example()


if __name__ == '__main__':
    main()


