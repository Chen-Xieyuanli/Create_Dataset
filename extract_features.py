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


class ExtractFeatures:
    '''Classifier for Creating dataset
    Input: The path of the dataset.
    Output: The Classnumber of each image.
    '''

    def __init__(self, path, confidence_coefficient=0.001):
        # the path of the dataset.
        self.path = path

        # set the confidence interval and delete the outside images
        self.confidence_coefficient = confidence_coefficient

        # set the numbers of the interval units
        self.number_of_intervals = 30

    def transform_image(self, img_path):
        normalize = T.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])

        transforms = T.Compose([
            T.Resize(size=(224, 224)),
            T.CenterCrop(224),
            T.ToTensor(),
            normalize
        ])
        try:
            Image.open(img_path)
            img = Image.open(img_path)
            img = img.convert("RGB")
            img = transforms(img)

            # show the transformed images
            if 0:
                img_ = img.numpy()
                img_ = np.transpose(img_, (1, 2, 0))
                plt.imshow(img_)
                plt.pause(0.1)

            # assign it to a variable
            img_var = Variable(img)
            img_var = img_var.unsqueeze(0)
            return img_var

        except:
            print("error1: Cannot open this image!!!")
            # os.remove(img_path)

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

    def saving_features(self):
        root_path = self.path
        image_list = os.listdir(root_path)
        image_list.sort()
        feature_txt_path = "./features.txt"  # save the feature list to the features.txt

        if os.path.exists(feature_txt_path):
            os.remove(feature_txt_path)

        f = open(feature_txt_path, "a+")

        for i in range(0, len(image_list)):
            image_path = os.path.join(root_path, image_list[i])
            if os.path.isfile(image_path):
                img_var = self.transform_image(image_path)

                if img_var is None:
                    print ("error2: The No." + str(image_list[i]) + " image is unreadable.")
                    try:
                        os.remove(image_path)
                        continue
                    except:
                        continue

                try:
                    # using ResNet to extract features of images
                    features = self.extract_features(img_var)
                    feature_slice = features[0, :, 0, 0].numpy()
                    new_context = str(image_list[i]) + " "
                    f.write(new_context)
                    for x in range(0, len(feature_slice)):
                        f.write(str(feature_slice[x])+" ")
                        pass
                    f.write("\n")
                    print("The No." + str(image_list[i]) + " image is done!")

                except:
                    print("error3: The No." + str(image_list[i]) + " image is unreadable.")
                    # os.remove(image_path)

        f.close()


# for test
if __name__ == '__main__':
    # dataset_path = " ".join(sys.argv[1:])
    dataset_path = "/home/ipb38admin/yuanli/Create_Dataset/cat"
    search = ExtractFeatures(dataset_path)
    search.saving_features()