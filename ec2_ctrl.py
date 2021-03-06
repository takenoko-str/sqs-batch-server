import botocore.exceptions
import time
from aws_handler import SQS, EC2


if __name__ == '__main__':
    my_filter = [{'Name': 'tag:AutoScaleGroup',
                  'Values': ['warmup']}]
    ec2 = EC2.describe(my_filter)
    sqs = SQS.sample()
    while True:
        msg = sqs.message_size()

        if int(msg) > 0:
            try:
                response = ec2.start(1)
            except botocore.exceptions.ClientError:
                print("error")

        if int(msg) == 0:
            try:
                response = ec2.stop(1)
            except botocore.exceptions.ClientError:
                print("error")
        time.sleep(5)
