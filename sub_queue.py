#!/usr/local/bin/python3

import json
import boto3
from os import environ as env
from settings import *

default_region = env.get('AWS_DEFAULT_REGION', 'ap-northeast-1')
session = boto3.session.Session(region_name=default_region)


class SubQueue:
    sns = session.client('sns')
    sqs = session.client('sqs')

    def __init__(self, topic_arn, queue_url, queue_arn, subscription_arn):
        self.topic_arn = topic_arn
        self.queue_url = queue_url
        self.queue_arn = queue_arn
        self.subscription_arn = subscription_arn

    @classmethod
    def create(cls, queue_name, topic_name):
        topic_arn = cls.sns.create_topic(
            Name=topic_name)["TopicArn"]

        queue_url = cls.sqs.create_queue(
            QueueName=queue_name)["QueueUrl"]

        queue_arn = cls.sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]

        subscription_arn = cls.sns.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=queue_arn,
        )["SubscriptionArn"]

        return cls(topic_arn, queue_url, queue_arn, subscription_arn)

    def set_subscription_attributes(self, model_name):
        attribute_value = {"model": [model_name]}
        self.sns.set_subscription_attributes(
            SubscriptionArn=self.subscription_arn,
            AttributeName='FilterPolicy',
            AttributeValue=json.dumps(attribute_value)
        )

    def set_queue_attributes(self):
        policy_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "MyPolicy",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "SQS:SendMessage",
                    "Resource": self.queue_arn,
                    "Condition": {
                        "ArnEquals": {
                            "aws:SourceArn": self.topic_arn
                        }
                    }
                }
            ]
        }
        self.sqs.set_queue_attributes(
            QueueUrl=self.queue_url,
            Attributes={
                'Policy': json.dumps(policy_json)
            }
        )


if __name__ == '__main__':
    model_names = ["queue_a", "queue_b", "queue_c"]
    for name in model_names:
        sub_queue = SubQueue.create(name, "model")
        sub_queue.set_subscription_attributes(name)
        sub_queue.set_queue_attributes()
