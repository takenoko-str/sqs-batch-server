# USAGE
# python stress_test.py

# import the necessary packages
from threading import Thread
import requests
import settings
import time
import sys

# initialize the Keras REST API endpoint URL along with the input
# image path
IMAGE_PATH = "beagle.png"
os.makedirs('logs', exist_ok=True)

# initialize the number of requests for the stress test along with
# the sleep amount between requests
NUM_REQUESTS = int(sys.argv[1])
SLEEP_COUNT = 0.05
x = []

def call_predict_endpoint(n):
    # load the input image and construct the payload for the request
    with open(IMAGE_PATH, "rb") as f:
        image = f.read()
        payload = {"image": image}
    print("[INFO] thread start")

    # submit the request
    r = requests.post(settings.KERAS_REST_API_URL, files=payload).json()

    # ensure the request was successful
    if r["success"]:
        print("[INFO] thread {} OK".format(n))
        with open("logs/stress_{}.log".format(n), 'a') as f:
            print(r["predictions"], file=f)

    # otherwise, the request failed
    else:
        print("[INFO] thread {} FAILED".format(n))

# loop over the number of threads
threads = []
for i in range(0, NUM_REQUESTS):
    # start a new thread to call the API
    t = Thread(target=call_predict_endpoint, args=(i,))
    #t.daemon = True
    threads.append(t)
    t.start()
    time.sleep(SLEEP_COUNT)

# insert a long sleep so we can wait until the server is finished
# processing the images
time.sleep(3)