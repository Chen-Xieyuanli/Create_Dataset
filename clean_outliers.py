#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

import os
import numpy as np
import torch.nn as nn
import matplotlib.pyplot as plt
import torchvision.models as models

from PIL import Image
from torch.autograd import Variable
from torchvision import transforms as T


class CleanOutliers():
    '''Classifier for Creating dataset
    Input: The path of dataset.
    Output: The Classnumber of each image.
    '''

    def __init__(self, path):
        self.path = path

    def transform_image(self, img_path):
        normalize = T.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])

        transforms = T.Compose([
            T.Resize(224),
            T.CenterCrop(224),
            T.ToTensor(),
            normalize
        ])
        try:
            Image.open(img_path)
            img = Image.open(img_path)
            img = img.convert("RGB")
            # assign it to a variable
            img_var = Variable(transforms(img))
            img_var = img_var.unsqueeze(0)
            return img_var

        except:
            print "Cannot open this image!!!"

    def extract_features(self, img_var):
        # set up the pretrained resnet
        resnet152 = models.resnet152(pretrained=True)
        modules = list(resnet152.children())[:-1]
        resnet152 = nn.Sequential(*modules)

        # get the output from the last hidden layer of the pretrained resnet
        features_var = resnet152(img_var)

        # get the tensor out of the variable
        features = features_var.data

        return features

    def clean_outliers(self):
        root_path = self.path
        image_list = os.listdir(root_path)
        for i in range(0, len(image_list)):
            image_path = os.path.join(root_path, image_list[i])
            if os.path.isfile(image_path):
                img_var = self.transform_image(image_path)

                if img_var is None:
                    print "The " + str(i) + "th image is unreadable."
                    continue

                try:
                    features = self.extract_features(img_var)
                    feature_slice = features[0, 1:, 0, 0].numpy()

                    feature_class = np.where(
                        feature_slice == np.max(feature_slice))

                    plt.plot(i, feature_class, 'ro', label="point")
                    print "plot " + str(i) + "th image."

                except:
                    print "The " + str(i) + "th image is unreadable."

        plt.show()


# for test
if __name__ == '__main__':
    dataset_path = " ".join(sys.argv[1:])
    # dataset_path = "/home/nubot/bonnet/create_dataset/downloads/cat"
    search = CleanOutliers(dataset_path)
    search.clean_outliers()
