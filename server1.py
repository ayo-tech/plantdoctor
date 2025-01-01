import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential


batch_size = 32
img_height = 180
img_width = 180
data_dir = "C:/Users/Ayo Gbadebo/Downloads/server/images/"

train_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
model = keras.models.load_model("imgrec.keras")

# test the model
def img_prediction(image_url):
    image_path = tf.keras.utils.get_file(origin=image_url)

    img = tf.keras.utils.load_img(
        image_path, target_size=(img_height, img_width)
    )
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    return "This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score))
    

n = 1
count = 0
for i in range(10000000):
    while n > 0:
        count += 1
        response_set = requests.get("https://cassavadiseases.pythonanywhere.com/m/api/upload_image/")
        resp = json.loads(response_set.text)
        print('running', count)
        for res in resp:
            if res['done'] == False:
                imgurl, imgid = res['image'], res['id']

                response = requests.get(imgurl)
                assert response.status_code == 200

                labelx = img_prediction(imgurl)
                responsex = requests.get("https://cassavadiseases.pythonanywhere.com/m/api/image_process/{idx}/{labeli}".format(idx=imgid, labeli=labelx))
                print(responsex)
