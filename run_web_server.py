from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
from aws_handler import S3, SQS, SNS
import numpy as np
import settings
import helpers
import flask
import redis
import uuid
import time
import json
import io
import os.path as op
from datetime import date

app = flask.Flask(__name__)
db = redis.StrictRedis(host=settings.REDIS_HOST,
                       port=settings.REDIS_PORT, 
                       db=settings.REDIS_DB)
s3 = S3.sample()
sqs = SQS.sample()
sns = SNS.sample()


def prepare_image(image, target):
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    return image


@app.route("/")
def homepage():
    return "Welcome to the PyImageSearch Keras REST API!"


@app.route("/predict/<name>", methods=["POST"])
def predict(name):
    data = {"success": False}

    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            response = flask.request.files["image"]
            data["filename"] = response.filename
            image = Image.open(io.BytesIO(response.read()))
            image = prepare_image(image,
                                  (settings.IMAGE_WIDTH, 
                                   settings.IMAGE_HEIGHT))

            # ensure our NumPy array is C-contiguous as well,
            # otherwise we won't be able to serialize it
            image = image.copy(order="C")

            imageID = str(uuid.uuid4())
            image = helpers.base64_encode_image(image)
            d = {"id": imageID, "image": image}

            # db.rpush(settings.IMAGE_QUEUE, json.dumps(d))
            today = str(date.today())
            s3_path = op.join(today, imageID)
            s3.put(s3_path, json.dumps(d))
            # sqs.send(imageID)
            sns.publish(s3_path, name)

            while True:
                # output = s3.get(imageID)
                output = db.get(imageID)

                if output is not None:
                    output = output.decode("utf-8")
                    data["predictions"] = json.loads(output)

                    db.delete(imageID)
                    break

                time.sleep(settings.CLIENT_SLEEP)

            data["success"] = True

    return flask.jsonify(data)


if __name__ == "__main__":
    print("* Starting web service...")
    app.run(host='0.0.0.0')

