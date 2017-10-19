import numpy as np
import os
import csv
import cv2
from generator import generator, get_manifest
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda, Dropout, Cropping2D, ELU
from keras.layers.pooling import MaxPooling2D
from keras.layers.convolutional import Conv2D
from keras.optimizers import Adam
import sys
import pickle

# parse arguments
if len(sys.argv)<2:
    driving_log='./data/combo-log.csv'
    print('Driving log (CSV) is '+driving_log)
elif len(sys.argv)==2:
    driving_log=sys.argv[1]
elif len(sys.argv)==3:
    driving_log=sys.argv[1]
    nb_epoch=int(sys.argv[2])
else:
    sys.exit()

# read the data and file manifest from csv log
samples = get_manifest(driving_log)
train_samples, validation_samples = train_test_split(samples, test_size=0.2)

# compile and train the model using the generator function
train_generator = generator(train_samples, batch_size=32)
validation_generator = generator(validation_samples, batch_size=32)

# keras neural network
# Define the model
model = Sequential()
model.add(Conv2D(3, 1, 1, input_shape=(90, 320, 3)))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Conv2D(3, 5, 5, subsample=(2, 2)))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Conv2D(24, 5, 5, subsample=(2, 2)))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Conv2D(36, 5, 5, subsample=(2, 2)))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Conv2D(48, 3, 3))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Conv2D(64, 3, 3))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Conv2D(128, 3, 3))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(100))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Dense(50))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Dense(10))
model.add(ELU())
model.add(Dropout(0.5))
model.add(Dense(1))
model.compile(loss='mse', optimizer=Adam(lr=0.0001))

# Number of epochs
if not 'nb_epoch' in locals(): 
    nb_epoch=100
print("Beginning fit to model over {} epochs".format(nb_epoch))
history = model.fit_generator(train_generator, samples_per_epoch= \
                  len(train_samples), validation_data=validation_generator, \
                  nb_val_samples=len(validation_samples), nb_epoch=nb_epoch)

model.save('model.h5')
pickle.dump(history.history, open('epoch-losses.p', "wb"))
