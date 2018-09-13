#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

import os
import sys
import threading
import numpy as np
import torch.nn as nn
import matplotlib.pyplot as plt
import torchvision.models as models

from PIL import Image
from torch.autograd import Variable
from torchvision import transforms as T


class CleanOutliers():
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
            T.Scale(224),
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
            print("Cannot open this image!!!")
            os.remove(img_path)

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

    def draw_distribution(self, feature_txt_path):
        filename = feature_txt_path
        features = {}
        valid_num = 0
        feature_sum = 0
        feature_list = []
        with open(filename, 'r') as file_to_read:
            plt.subplot(211)
            while True:
                lines = file_to_read.readline()
                if not lines:
                    break

                try:
                    p_tmp, E_tmp = [float(i) for i in lines.split(':')]
                    features[p_tmp] = E_tmp
                    valid_num += 1
                    feature_sum += E_tmp
                    feature_list.append(E_tmp)
                    plt.plot(p_tmp, E_tmp, 'ro', label="point")
                except:
                    pass

        # calculate the mean and variance of the feature list
        feature_mean = feature_sum / valid_num
        tmp = [(i - feature_mean) * (i - feature_mean) for i in feature_list]
        feature_variance = np.sum(tmp) / valid_num

        # plot the line of the mean value and the confidence interval
        x = np.arange(0, 3000, 0.1)
        plt.plot(x, feature_mean * np.ones(30000), "b", linewidth=2.0)
        plt.plot(x, (feature_mean + self.confidence_coefficient) * np.ones(30000), "b--", linewidth=2.0)
        plt.plot(x, (feature_mean - self.confidence_coefficient) * np.ones(30000), "b--", linewidth=2.0)
        plt.title("Medians of features", fontsize="large", fontweight="bold")
        plt.xlabel("image_number", fontweight="bold")
        plt.ylabel("median_value", fontweight="bold")

        # plot the distribution and the confidence interval
        plt.subplot(212)
        num_interval_array = []
        x_array = []
        x_value = np.min(feature_list)
        lenth_of_interval = (np.max(feature_list) - np.min(feature_list)) / self.number_of_intervals

        while x_value < np.max(feature_list):
            num_interval = np.extract(np.where(np.extract(np.where(feature_list < x_value + lenth_of_interval),
                                                          feature_list) > x_value), feature_list)
            x_value += lenth_of_interval
            num_interval_array.append(num_interval.size)
            x_array.append(x_value)

        plt.plot(x_array, num_interval_array, "r", linewidth=2.0)
        plt.plot(feature_mean * np.ones(np.max(num_interval_array)), np.arange(0, np.max(num_interval_array), 1), "b", linewidth=2.0)
        plt.plot((feature_mean + self.confidence_coefficient) * np.ones(np.max(num_interval_array)), np.arange(0, np.max(num_interval_array), 1), "b--", linewidth=2.0)
        plt.plot((feature_mean - self.confidence_coefficient) * np.ones(np.max(num_interval_array)), np.arange(0, np.max(num_interval_array), 1), "b--", linewidth=2.0)
        plt.title("Feature Distribution", fontsize="large", fontweight="bold")
        plt.xlabel("median_value", fontweight="bold")
        plt.ylabel("number_of_images", fontweight="bold")

        # returns the number of the images to delete
        delete_list = np.where(feature_list > np.float64(feature_mean + self.confidence_coefficient))[-1].tolist()
        delete_list.append(np.where(feature_list < np.float64(feature_mean - self.confidence_coefficient))[-1].tolist())

        return delete_list

    def pca(dataMat, topNfeat=3):
        # calculate the mean value of each column
        feature_mean = np.mean(dataMat, axis=0)

        # decentralization
        feature_decentralized = dataMat - feature_mean

        # calculate the covariance
        # set each column representing a variable, while the rows contain observations.
        cov_mat = np.cov(feature_decentralized, rowvar=0)

        # calculate the eigenvalues of the covariance matrix and the corresponding eigenvectors
        eig_vals, eig_vects = np.linalg.eig(np.mat(cov_mat))

        # descend the eigenvalues
        eig_val_id = np.argsort(eig_vals)
        eig_val_id = eig_val_id[:-(topNfeat + 1):-1]

        # extract the corresponding eigenvectors
        red_eig_vects = eig_vects[:, eig_val_id]

        # descend the dimensions
        low_data_mat = feature_decentralized * red_eig_vects

        return low_data_mat, feature_mean

    def clean_outliers(self):
        root_path = self.path
        image_list = os.listdir(root_path)
        image_list.sort()
        feature_txt_path = "./features.txt" # save the feature list to the features.txt
        f = open(feature_txt_path, "a+")

        # Init the feature matrix
        # each row represents the feature of one image
        # each column represents the values of a specific dimension in all features
        feature_matrix = [[]] * len(image_list)

        for i in range(0, len(image_list)):
            image_path = os.path.join(root_path, image_list[i])
            if os.path.isfile(image_path):
                img_var = self.transform_image(image_path)

                if img_var is None:
                    print ("The No." + str(image_list[i]) + " image is unreadable.")
                    new_context = str(image_list[i]) + ": is bad\n"
                    f.write(new_context)
                    try:
                        os.remove(image_path)
                        continue
                    except:
                        continue

                try:
                    # using ResNet to extract features of images
                    features = self.extract_features(img_var)
                    feature_slice = features[0, 1:, 0, 0].numpy()

                    # record all the features as a matrix
                    # feature_matrix[image_list[i]] = feature_slice

                    # feature_class = np.mean(feature_slice)

                    new_context = str(image_list[i]) + " "
                    f.write(new_context)
                    for x in range(0, len(feature_slice)):
                        f.write(str(feature_slice[x])+" ")
                        pass
                    f.write("\n")

                    print("The No." + str(image_list[i]) + " image is done!")

                except:
                    print("The No." + str(image_list[i]) + " image is unreadable.")
                    new_context = str(image_list[i]) + ": is bad\n"
                    f.write(new_context)
                    # os.remove(image_path)

        f.close()

        # draw the distribution of the features' medians and delete the outliers
        delete_list = self.draw_distribution(feature_txt_path)
        for i in range(0, len(delete_list)):
            print("delete " + str(image_list[i]))
            try:
                continue
                # os.remove(os.path.join(root_path, image_list[i]))
            except:
                continue

        # show the distribution of the features
        plt.show()


# for test
if __name__ == '__main__':
    # dataset_path = " ".join(sys.argv[1:])
    dataset_path = "/home/ipb38admin/yuanli/Create_Dataset/car"
    search = CleanOutliers(dataset_path)
    search.clean_outliers()
