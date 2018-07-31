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
s3 = S3(settings.S3_BUCKET)
sqs = SQS(settings.SQS_URL)


def classify_process():
    print("* Loading model...")
    model = ResNet50(weights="imagenet")
    print("* Model loaded")

    while True:
        
        messages = sqs.receive()
        images = []
        if not messages:
            continue

        for msg in messages:
            body = json.loads(msg['Body'])
            s3_path = body['Message']
            img = s3.get(s3_path)
            images.append(img)

        # images = db.lrange(settings.IMAGE_QUEUE, 0,
        #                    settings.BATCH_SIZE - 1)
        
        image_ids = []
        image_batch = None

        for img in images:

            img = json.loads(img.decode("utf-8"))
            image = helpers.base64_decode_image(img["image"],
                                                settings.IMAGE_DTYPE,
                                                (1, settings.IMAGE_HEIGHT, 
                                                    settings.IMAGE_WIDTH,
                                                    settings.IMAGE_CHANS))

            if image_batch is None:
                image_batch = image

            else:
                image_batch = np.vstack([image_batch, image])

            image_ids.append(img["id"])

        if len(image_ids) > 0:

            print("* Batch size: {}".format(image_batch.shape))
            predicts = model.predict(image_batch)
            results = imagenet_utils.decode_predictions(predicts)

            for (image_id, result_set) in zip(image_ids, results):

                output = []

                for _, label, prob in result_set:
                    r = {"label": label, "probability": float(prob)}
                    output.append(r)

                db.set(image_id, json.dumps(output))

            # db.ltrim(settings.IMAGE_QUEUE, len(imageIDs), -1)
        sqs.delete(messages)

        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    classify_process()

