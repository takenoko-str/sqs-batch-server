from celery import Celery
import os
from settings import *

BROKER_URL = 'sqs://{}:{}@'.format(os.environ['AWS_SQS_ACCESS_KEY'], os.environ['AWS_SQS_SECRET_ACCESS_KEY'])
app = Celery('tasks', broker=BROKER_URL)


@app.task
def add(x, y):
    return x, y

