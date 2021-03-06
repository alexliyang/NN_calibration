# Code example from https://github.com/sebastianbk/finetuned-resnet50-keras/blob/master/resnet50_train.py

import math, json, os, sys

import keras
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Dense
from keras.models import Model
from keras.optimizers import Adam
from keras.preprocessing import image
import pickle
from sklearn.model_selection import train_test_split
from load_data_cars import load_data_cars
from image_gen_extended import ImageDataGenerator, random_crop


SIZE_IMG = (256, 256)
SIZE_CROP = (224, 224)
BATCH_SIZE = 64
SEED = 333
NR_CLASSES = 196  # Classes for cars?
EPOCHS = 250
SEED = 333  # Random seed for reproducibility

# Train 8144 and test 8041

# Issue about random crop
# https://github.com/keras-team/keras/issues/3338

if __name__ == "__main__":

    print("Load data")
    
    (x_train, y_train), (x_test, y_test) = load_data_cars(SIZE_IMG, SIZE_CROP)
    
    y_train = keras.utils.to_categorical(y_train, NR_CLASSES)
    y_test = keras.utils.to_categorical(y_test, NR_CLASSES)
    
    x_test50, x_val, y_test50, y_val = train_test_split(x_test, y_test, test_size=0.5, random_state=SEED)
    
    #  If you are freezing initial layers, you should use imagenet mean/std. (https://discuss.pytorch.org/t/confused-about-the-image-preprocessing-in-classification/3965)
    
    img_mean = x_train.mean(axis=(0,1,2))  # per-channel mean, should use imagenet means?
    x_train = (x_train-img_mean)
    x_val = (x_val-img_mean)
    x_test50 = (x_test50-img_mean)
    
    # set data augmentation
    print('Using real-time data augmentation.')
    datagen = ImageDataGenerator(horizontal_flip=True,)
    datagen.config['random_crop_size'] = SIZE_CROP

    datagen.set_pipeline([random_crop])
    # Add random crop for training
    datagen.fit(x_train) 
    
    print("Load model")
    model = keras.applications.resnet50.ResNet50()  # Load in pretrained model (ImageNet)

    model.layers.pop()  # Remove last layer
    for layer in model.layers:
        layer.trainable=False  # Set model layers untrainable
        
    last = model.layers[-1].output  # Get last layer
    
    x = Dense(NR_CLASSES, activation="softmax")(last)  # Add new trainable Dense layer in the end.
    model = Model(model.input, x)
    model.compile(optimizer=Adam(lr=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

    early_stopping = EarlyStopping(patience=10)
    checkpointer = ModelCheckpoint('resnet50_cars_best.h5', verbose=1, save_best_only=True)
    cbks = [early_stopping, checkpointer]

    print("Start training")
    hist = model.fit_generator(datagen.flow(x_train, y_train, batch_size=BATCH_SIZE),
                         steps_per_epoch=len(x_train) // BATCH_SIZE,
                         epochs=epochs,
                         callbacks=cbks,
                         validation_data=(x_val, y_val))
                         
    model.save('resnet50_cars.h5')
    
    print("Get test accuracy:")
    loss, accuracy = model.evaluate(x_test50, y_test50, verbose=0)
    print("Test: accuracy1 = %f  ;  loss1 = %f" % (accuracy, loss))
    
    print("Pickle models history")
    with open('hist_resnet50_cars.p', 'wb') as f:
        pickle.dump(hist.history, f)