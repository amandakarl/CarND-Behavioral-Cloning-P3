import cv2
import csv
import numpy as np
import sklearn

# Get the manifest of image filenames
def get_manifest(filename):
    samples = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            samples.append(line)
    # Omit the first line as it has no data
    return samples[1:]

# Data augmentation
def random_augment(batch_sample, flip_prob=0.5, lcr_prob=None):

    # Choose the camera type
    choice = np.random.choice(3, lcr_prob)
    name = batch_sample[choice].strip()

    # Read the image and add offset to direction 
    image = cv2.imread(name)
    angle = float(batch_sample[3])+[0.0,0.15,-.15][choice]

    # Flip image
    if np.random.binomial(1,flip_prob):
        image = np.fliplr(image)
        angle = -angle

    return image, angle

# Generator to feed the neural network
def generator(samples, batch_size=32):

    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        sklearn.utils.shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]
            images = []
            angles = []
            for batch_sample in batch_samples:
                image, angle = random_augment(batch_sample)
                images.append(image)
                angles.append(angle)

            # trim image to only see section with road
            X_train = np.array(images)
            y_train = np.array(angles)
            yield sklearn.utils.shuffle(X_train, y_train)

