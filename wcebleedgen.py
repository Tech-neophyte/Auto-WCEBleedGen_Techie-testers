# -*- coding: utf-8 -*-
"""WCEBleedGen.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X_0LGPP4Y-gV-vZ3j3YU92GuuZnVhsDy
"""

#hello

"""Training dataset"""

!wget https://zenodo.org/record/7548320/files/WCEBleedGen.zip?download=1 -O dataset

!unzip dataset -d "images/"

import os
import numpy as np
import matplotlib.pyplot as plt

classes=os.listdir("images/WCEBleedGen")
classes

classes.pop(2)
classes

import os
current_folder_path = '/content/images/WCEBleedGen/bleeding/Images'

new_folder_name = 'images'

os.rename(current_folder_path, os.path.join(os.path.dirname(current_folder_path), new_folder_name))

len(os.listdir("images/WCEBleedGen/bleeding/images"))

len(os.listdir("images/WCEBleedGen/non-bleeding/images"))

for c in classes:
  print(c,len(os.listdir("images/WCEBleedGen/"+c+"/images")))

"""Data loading"""

from tensorflow.keras import utils

utils.load_img("/content/images/WCEBleedGen/bleeding/Annotations/ann- (10).png")

utils.load_img("/content/images/WCEBleedGen/non-bleeding/images/img- (10).png",target_size=(200,200))

img=utils.load_img("/content/images/WCEBleedGen/bleeding/images/img- (1).png",target_size=(200,200))

img=np.array(img)
img.shape

train_data=[]
train_labels=[]
for category in classes:
    folder="/content/images/WCEBleedGen/"+category+"/images"
    for img_name in os.listdir(folder):
      img_path=folder+"/"+img_name
      img=utils.load_img(img_path,target_size=(200,200))
      img=np.array(img)
      train_data.append(img)
      train_labels.append(category)

X=np.array(train_data)
Y=np.array(train_labels)

import sklearn
from sklearn.model_selection import train_test_split

X_train,X_test,Y_train,Y_test=train_test_split( X,Y,test_size=0.2,random_state=42)

X_train.shape

Y_train.shape

plt.imshow(X_train[20])

Y_train[20]

category2label={"bleeding":0 , "non-bleeding":1}
label2category={0:"bleeding" , 1:"non-bleeding"}

Y_train=np.array([category2label[label] for label in Y_train])

Y_train[-5:]

from tensorflow.keras.utils import to_categorical

Y_train_new = to_categorical(Y_train)
Y_train_new.shape

from google.colab.patches import cv2_imshow
import cv2

image = cv2.imread('/content/images/WCEBleedGen/bleeding/images/img- (100).png')
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower_red = (0, 100, 100)
upper_red = (10, 255, 255)

mask = cv2.inRange(hsv_image, lower_red, upper_red)

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

min_area_threshold = 10
confidence_threshold = 0.01
bounding_boxes = []

for contour in contours:
    area = cv2.contourArea(contour)
    if area > min_area_threshold:
        confidence = area / (image.shape[0] * image.shape[1])

        if confidence >= confidence_threshold:
            x, y, w, h = cv2.boundingRect(contour)
            bounding_box = (x, y, x + w, y + h)
            bounding_boxes.append((bounding_box, confidence))

for idx, (bbox, confidence) in enumerate(bounding_boxes):
    x1, y1, x2, y2 = bbox
    print(f"Region {idx + 1}:")
    print(f"  Bounding Box Coordinates: ({x1}, {y1}) to ({x2}, {y2})")
    print(f"  Confidence Level: {confidence}")

for (bbox, confidence) in bounding_boxes:
    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
cv2_imshow(image)

def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    intersection_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    boxA_area = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxB_area = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = intersection_area / float(boxA_area + boxB_area - intersection_area)
    return iou

print(calculate_iou((x, y, x + w, y + h),(x1,y1,x2,y2)))

from tensorflow.keras import Sequential # we want to create sequential model.
from tensorflow.keras.layers import Dense # fully connected layer
from tensorflow.keras.layers import Convolution2D, MaxPooling2D, Flatten

model = Sequential()


model.add(Convolution2D(64, (3,3), activation='relu', input_shape =(200, 200 ,3) ))
model.add(Convolution2D(64, (3,3), activation='relu' ))
model.add(MaxPooling2D())
model.add(Convolution2D(128, (3,3), activation='relu' ))
model.add(MaxPooling2D())
model.add(Flatten())
model.add(Dense(2, activation = 'softmax'))

model.summary()

model.compile(loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X_train, Y_train_new, batch_size=128, epochs=10,validation_split=0.2)

[test_loss, test_acc] = model.evaluate(X_train, Y_train_new)
print("Evaluation result on Test Data : Loss = {}, accuracy = {}".format(test_loss, test_acc))

Y_test.shape

Y_test=np.array([category2label[label] for label in Y_test])
Y_test_new = to_categorical(Y_test)
Y_test_new.shape

predictions_probabilities = model.predict(X_test)
threshold = 0.5
predictions_binary = (predictions_probabilities > threshold).astype(int)
print(predictions_binary)

"""Accuracy"""

[test_loss, test_acc] = model.evaluate(X_test, Y_test_new)
print("Evaluation result on Test Data : Loss = {}, accuracy = {}".format(test_loss, test_acc))

def bounding_box(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red = (0, 100, 100)
    upper_red = (10, 255, 255)

    mask = cv2.inRange(hsv_image, lower_red, upper_red)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area_threshold = 10
    confidence_threshold = 0.01
    bounding_boxes = []

    for contour in contours:
      area = cv2.contourArea(contour)
      if area > min_area_threshold:
          confidence = area / (image.shape[0] * image.shape[1])

          if confidence >= confidence_threshold:
              x, y, w, h = cv2.boundingRect(contour)
              bounding_box = (x, y, x + w, y + h)
              bounding_boxes.append((bounding_box, confidence))

    for idx, (bbox, confidence) in enumerate(bounding_boxes):
      x1, y1, x2, y2 = bbox
      print(f"Region {idx + 1}:")
      print(f"  Bounding Box Coordinates: ({x1}, {y1}) to ({x2}, {y2})")
      print(f"  Confidence Level: {confidence}")

    for (bbox, confidence) in bounding_boxes:
      x1, y1, x2, y2 = bbox
      cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2_imshow(image)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (100).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (1130).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (1145).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (1260).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (134).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (132).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (148).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (150).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (240).png")
bounding_box(image20)

image20 = cv2.imread("/content/images/WCEBleedGen/bleeding/images/img- (36).png")
bounding_box(image20)





actual_labels = Y_test_new
predicted_labels = model.predict(X_test)

TP = np.sum((actual_labels == 1) & (predicted_labels == 1))
TN = np.sum((actual_labels == 0) & (predicted_labels == 0))
FP = np.sum((actual_labels == 0) & (predicted_labels == 1))
FN = np.sum((actual_labels == 1) & (predicted_labels == 0))

print(f"True Positives (TP): {TP}")
print(f"True Negatives (TN): {TN}")
print(f"False Positives (FP): {FP}")
print(f"False Negatives (FN): {FN}")

accuracy=(TP+TN)/(TP+TN+FP+FN)
print(accuracy)

recall=TP/(TP+FN)
print(recall)

precision=TP/(TP+FP)
precision

f1score=(2 * precision * recall) / (precision + recall)
f1score



from google.colab import drive
drive.mount('/content/drive')

path="/content/drive/My Drive/Misahub/Test Dataset 1"

import os
files = os.listdir(path)

from tensorflow.keras import utils

classes=os.listdir("images/WCEBleedGen")
classes

classes.pop(2)
classes

test_1_data=[]
test_1_labels=[]
for category in classes:
    folder=path
    for img_name in os.listdir(folder):
      img_path=folder+"/"+img_name
      img=utils.load_img(img_path,target_size=(200,200))
      img=np.array(img)
      test_1_data.append(img)
      test_1_labels.append(category)

X_test1=np.array(test_1_data)
Y_test1=np.array(test_1_labels)

X_test1.shape

Y_test1.shape

from tensorflow.keras.utils import to_categorical

category2label={"bleeding":0 , "non-bleeding":1}
label2category={0:"bleeding" , 1:"non-bleeding"}

Y_test1=np.array([category2label[label] for label in Y_test1])

Y_test1_new = to_categorical(Y_test1)
Y_test1_new.shape

predictions_probabilities = model.predict(X_test1)
threshold = 0.5
predictions_binary = (predictions_probabilities > threshold).astype(int)
print(predictions_binary)

image1 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 1/A0047.png")
bounding_box(image1)

image2 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 1/A0042.png")
bounding_box(image2)

image3 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 1/A0036.png")
bounding_box(image3)

image4 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 1/A0038.png")
bounding_box(image4)

image5 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 1/A0034.png")
bounding_box(image5)



path2="/content/drive/My Drive/Misahub/Test Dataset 2"

files = os.listdir(path2)

test2_data=[]
test2_labels=[]
for category in classes:
    folder=path2
    for img_name in os.listdir(folder):
      img_path=folder+"/"+img_name
      img=utils.load_img(img_path,target_size=(200,200))
      img=np.array(img)
      test2_data.append(img)
      test2_labels.append(category)

X_test2=np.array(test2_data)
Y_test2=np.array(test2_labels)

from tensorflow.keras.utils import to_categorical

category2label={"bleeding":0 , "non-bleeding":1}
label2category={0:"bleeding" , 1:"non-bleeding"}

Y_test2.shape

model.predict(X_test2)

predictions_probabilities1 = model.predict(X_test2)
threshold = 0.5
predictions_binary = (predictions_probabilities > threshold).astype(int)
print(predictions_binary)

folder_path = '/content/drive/MyDrive/Misahub/Test Dataset 2'

image_names = os.listdir(folder_path)

image_names = [file for file in image_names if file.endswith(('.png'))]


labels = [sublist[0] for sublist in predictions_binary]

bleeding_image_names = [image for image, label in zip(image_names, labels) if (label) == 1]

print(bleeding_image_names)





image6 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 2/A0050.png")
bounding_box(image6)

image7 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 2/A0051.png")
bounding_box(image7)

image8 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 2/A0061.png")
bounding_box(image8)

image9 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 2/A0375.png")
bounding_box(image9)

image10 = cv2.imread("/content/drive/MyDrive/Misahub/Test Dataset 2/A0433.png")
bounding_box(image10)



