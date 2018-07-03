#!/usr/local/bin/python3

import boto3


class EC2:
    client = boto3.client('ec2', region_name='ap-northeast-1')

    def __init__(self, ids):
        self.ids = ids

    @classmethod
    def describe(cls, filters, ids=[]):
        response = cls.client.describe_instances(Filters=filters)
        for reservation in response.get('Reservations', [{}]):
            for instance in reservation.get('Instances', [{}]):
                ids.append(instance.get('InstanceId'))
        return cls(ids)

    def start(self):
        self.client.start_instances(InstanceIds=self.ids)

    def stop(self):
        self.client.stop_instances(InstanceIds=self.ids)
