# Used https://github.com/titu1994/Wide-Residual-Networks as base

import numpy as np
import sklearn.metrics as metrics

import wide_residual_network as wrn
from keras.datasets import cifar100
import keras.callbacks as callbacks
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import plot_model
from sklearn.model_selection import train_test_split


from keras import backend as K
import pickle

batch_size = 100
nb_epoch = 125
img_rows, img_cols = 32, 32
nb_classes = 100
seed = 333

# Add here data loading
# data
(X_train, Y_train), (X_test, y_test) = cifar100.load_data()
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
#X_train = np.transpose(X_train.astype('float32'), (0, 3, 1, 2))  # Channels first
#X_test = np.transpose(X_test.astype('float32'), (0, 3, 1, 2))  # Channels first


# Data splitting (get additional 5k validation set)
# Sklearn to split
X_train45, x_val, Y_train45, y_val = train_test_split(X_train, Y_train, test_size=0.1, random_state=seed)  # random_state = seed

img_mean = X_train45.mean(axis=0)  # per-pixel mean
X_train45 = X_train45-img_mean
x_val = x_val-img_mean
X_test = X_test-img_mean


img_gen = ImageDataGenerator(
    horizontal_flip=True,
    width_shift_range=0.125,  # 0.125*32 = 4 so max padding of 4 pixels, as described in paper.
    height_shift_range=0.125,
    fill_mode="constant",
    cval = 0
)

img_gen.fit(X_train45)
Y_train45 = np_utils.to_categorical(Y_train45, nb_classes)  # 1-hot vector
y_val = np_utils.to_categorical(y_val, nb_classes)
y_test = np_utils.to_categorical(y_test, nb_classes)


init_shape = (3, 32, 32) if K.image_dim_ordering() == 'th' else (32, 32, 3)

# For WRN-16-8 put N = 2, k = 8
# For WRN-28-10 put N = 4, k = 10
# For WRN-40-4 put N = 6, k = 4
model = wrn.create_wide_residual_network(init_shape, nb_classes=nb_classes, N=2, k=4, dropout=0.00)

model.summary()
#plot_model(model, "WRN-16-8.png", show_shapes=False)

model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["acc"])
print("Finished compiling")

#model.load_weights("weights/WRN-16-8 Weights.h5")
print("Model loaded.")

hist = model.fit_generator(img_gen.flow(X_train45, Y_train45, batch_size=batch_size, shuffle=True),
                   steps_per_epoch=len(X_train45) // batch_size, epochs=nb_epoch,
                   callbacks=[callbacks.ModelCheckpoint("WRN_16_4_Weights_cifar100.h5",
                                                        monitor="val_acc",
                                                        save_best_only=True,
                                                        verbose=1)],
                   validation_data=(x_val, y_val),
                   validation_steps=x_val.shape[0] // batch_size,)
                   
model.save_weights('model_weight_ep125_wide16_4_cifar_100.hdf5')


yPreds = model.predict(X_test)
yPred = np.argmax(yPreds, axis=1)
yPred = np_utils.to_categorical(yPred)
yTrue = y_test

accuracy = metrics.accuracy_score(yTrue, yPred) * 100
error = 100 - accuracy
print("Accuracy : ", accuracy)
print("Error : ", error)

print("Get test accuracy:")
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print("Test: accuracy1 = %f  ;  loss1 = %f" % (accuracy, loss))

print("Pickle models history")
with open('hist_wide16_4_cifar100.p', 'wb') as f:
    pickle.dump(hist.history, f)
