# coding=utf-8
from threading import Thread
from typing import IO
import requests
import settings
import logging
import time
import sys
import os

IMAGE_PATH = "beagle.png"
os.makedirs('logs', exist_ok=True)
NUM_REQUESTS = int(sys.argv[1])
SLEEP_COUNT = 0.05
x = []
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


def call_predict_endpoint(n):
    with open(IMAGE_PATH, "rb") as f:
        image = f.read()
        payload = {"image": image}
    logging.debug("thread {} GO".format(n))

    r = requests.post(settings.KERAS_REST_API_URL, files=payload).json()

    if r["success"]:
        logging.debug("thread {} OK".format(n))
        with open("logs/stress_{}.log".format(n), 'a') as f:  # type: IO[str]
            print(r["predictions"], file=f)

    else:
        logging.debug("thread {} FAILED".format(n))

threads = []
for i in range(0, NUM_REQUESTS):
    t = Thread(target=call_predict_endpoint, args=(i,))
    # t.daemon = True
    threads.append(t)
    t.start()
    time.sleep(SLEEP_COUNT)

time.sleep(3)