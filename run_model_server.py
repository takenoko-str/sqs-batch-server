# import the necessary packages
from keras.applications import ResNet50
from keras.applications import imagenet_utils
import numpy as np
import settings
import helpers
import redis
import time
import json
from aws_handler import SQS, S3


db = redis.StrictRedis(host=settings.REDIS_HOST,
                       port=settings.REDIS_PORT, 
                       db=settings.REDIS_DB)
sqs = SQS.sample()
s3 = S3.sample()


def classify_process():
    print("* Loading model...")
    model = ResNet50(weights="imagenet")
    print("* Model loaded")

    while True:
        
        messages = sqs.receive(10)
        queue = []
        if not messages:
            continue

        for msg in messages:
            body = json.loads(msg['Body'])
            s3_path = body['Message']
            q = s3.get(s3_path)
            queue.append(q)

        # queue = db.lrange(settings.IMAGE_QUEUE, 0,
        #                   settings.BATCH_SIZE - 1)
        
        imageIDs = []
        batch = None

        for q in queue:

            q = json.loads(q.decode("utf-8"))
            image = helpers.base64_decode_image(q["image"],
                                                settings.IMAGE_DTYPE,
                                                (1, settings.IMAGE_HEIGHT, 
                                                    settings.IMAGE_WIDTH,
                                                    settings.IMAGE_CHANS))

            if batch is None:
                batch = image

            else:
                batch = np.vstack([batch, image])

            imageIDs.append(q["id"])

        if len(imageIDs) > 0:

            print("* Batch size: {}".format(batch.shape))
            preds = model.predict(batch)
            results = imagenet_utils.decode_predictions(preds)

            for (imageID, resultSet) in zip(imageIDs, results):

                output = []

                for (imagenetID, label, prob) in resultSet:
                    r = {"label": label, "probability": float(prob)}
                    output.append(r)

                db.set(imageID, json.dumps(output))

            # db.ltrim(settings.IMAGE_QUEUE, len(imageIDs), -1)
        sqs.delete(messages)

        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    classify_process()

