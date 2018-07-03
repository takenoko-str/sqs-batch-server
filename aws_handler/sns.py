#!/usr/local/bin/python3

import os
import boto3


class SNS:
    TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

    def __init__(self, topic_arn):
        self.client = boto3.client('sns', region_name='ap-northeast-1')
        self.topic_arn = topic_arn

    @classmethod
    def sample(cls):
        return cls(cls.TOPIC_ARN)

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


def sns_example():
    sns = SNS.sample()
    sns.publish('Male, 33 years old', 'test')
