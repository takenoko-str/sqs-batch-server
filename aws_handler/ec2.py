#!/usr/local/bin/python3

import boto3
import random


class EC2:
    client = boto3.client('ec2', region_name='ap-northeast-1')

    def __init__(self, instances):
        self.instances = instances

    @classmethod
    def describe(cls, filters):
        instances = {}
        response = cls.client.describe_instances(Filters=filters)
        for reservation in response.get('Reservations', [{}]):
            for instance in reservation.get('Instances', [{}]):
                instance_id = instance.get('InstanceId')
                state = instance.get('State')['Name']
                instances[instance_id] = state
        return cls(instances)

    def start(self, num=100):
        start_instances = []
        for instance_id, state in self.instances.items():
            if state == 'stopped':
                start_instances.append(instance_id)

        if len(start_instances) < num:
            num = len(start_instances)

        start_instances = random.sample(start_instances, num)
        self.client.start_instances(InstanceIds=start_instances)

    def stop(self, num=100):
        stop_instances = []
        for instance_id, state in self.instances.items():
            if state == 'running':
                stop_instances.append(instance_id)

        if len(stop_instances) < num:
            num = len(stop_instances)

        stop_instances = random.sample(stop_instances, num)
        self.client.stop_instances(InstanceIds=stop_instances)

