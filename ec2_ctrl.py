import botocore.exceptions
from aws_handler import SQS, EC2


if __name__ == '__main__':
    my_filter = [{'Name': 'tag:AutoScaleGroup',
                  'Values': ['warmup']}]
    ec2 = EC2.describe(my_filter)
    sqs = SQS.sample()
    msg = sqs.message_size()

    if int(msg) > 0:
        try:

            response = ec2.start()
        except botocore.exceptions.ClientError:
            print("error")

    if int(msg) == 0:
        try:
            response = ec2.stop()
        except botocore.exceptions.ClientError:
            print("error")
