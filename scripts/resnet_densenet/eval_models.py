from __future__ import print_function

import os.path

import densenet
import numpy as np
import sklearn.metrics as metrics

from keras.datasets import cifar10, cifar100
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD
from keras.callbacks import LearningRateScheduler
from keras import backend as K
from sklearn.model_selection import train_test_split
from calibration import evaluate_model


batch_size = 64
nb_classes10 = 10
nb_classes100 = 100

nb_epoch = 300

img_rows, img_cols = 32, 32
img_channels = 3

img_dim = (img_channels, img_rows, img_cols) if K.image_dim_ordering() == "th" else (img_rows, img_cols, img_channels)
depth = 40
nb_dense_block = 3
growth_rate = 12
nb_filter = -1
dropout_rate = 0.0 # 0.0 for data augmentation
seed = 333
weight_decay = 0.0001
learning_rate = 0.1

weights_file_10 =  "../../models/weights_densenet_16_8_c10.h5"
weights_file_100 =  "../../models/weights_densenet_16_8_c100.h5"



# CIFAR-10 ===================

print("Evaluate CIFAR-10 densenet.")

model = densenet.DenseNet(img_dim, classes=nb_classes10, depth=depth, nb_dense_block=nb_dense_block,
                          growth_rate=growth_rate, nb_filter=nb_filter, dropout_rate=dropout_rate, weights=None, weight_decay=1e-4)

                          
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

x_train45, x_val, y_train45, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=seed)  # random_state = seed

#For data preprocessing, we normalize the data using the channel means and standard deviations (https://arxiv.org/pdf/1608.06993v3.pdf)

img_mean = x_train45.mean(axis=0)  # per-pixel mean
img_std = x_train45.std(axis=0)  # std
x_train45 = (x_train45-img_mean)/img_std
x_val = (x_val-img_mean)/img_std
x_test = (x_test-img_mean)/img_std

y_train45 = np_utils.to_categorical(y_train45, nb_classes10)  # 1-hot vector
y_val = np_utils.to_categorical(y_val, nb_classes10)
y_test = np_utils.to_categorical(y_test, nb_classes10)
evaluate_model(model, weights_file_10, x_test, y_test, bins = 15, verbose = True)



# CIFAR-100 ===================

print("Evaluate CIFAR-100 densenet.")

model = densenet.DenseNet(img_dim, classes=nb_classes100, depth=depth, nb_dense_block=nb_dense_block,
                          growth_rate=growth_rate, nb_filter=nb_filter, dropout_rate=dropout_rate, weights=None, weight_decay=1e-4)

                          
(x_train, y_train), (x_test, y_test) = cifar100.load_data()

x_train45, x_val, y_train45, y_val = train_test_split(x_train, y_train, test_size=0.1, random_state=seed)  # random_state = seed

#For data preprocessing, we normalize the data using the channel means and standard deviations (https://arxiv.org/pdf/1608.06993v3.pdf)

img_mean = x_train45.mean(axis=0)  # per-pixel mean
img_std = x_train45.std(axis=0)  # std
x_train45 = (x_train45-img_mean)/img_std
x_val = (x_val-img_mean)/img_std
x_test = (x_test-img_mean)/img_std

y_train45 = np_utils.to_categorical(y_train45, nb_classes100)  # 1-hot vector
y_val = np_utils.to_categorical(y_val, nb_classes100)
y_test = np_utils.to_categorical(y_test, nb_classes100)
evaluate_model(model, weights_file_100, x_test, y_test, bins = 15, verbose = True)
