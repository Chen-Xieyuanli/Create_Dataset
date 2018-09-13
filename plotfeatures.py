#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet
import os
import sys
# import cv
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from PIL import Image, ImageTk
from mpl_toolkits.mplot3d import Axes3D

def nothing(a):
    pass

def pass_image(a, b):
    global i_select
    i_select += 1
    pass

def input_yes(a, b):
    global i_select
    print("i_select: ", i_select)
    selected_image = feature_matrix[i_select]
    selected_images.append(selected_image)
    i_select += 1


def take_first(elem):
    return elem[0]

def calEuclideanDistance(vec1,vec2):
    dist = np.sqrt(np.sum(np.square(vec1 - vec2)))
    return dist

def pca(dataMat, topNfeat=3):
    # calculate the mean value of each column
    feature_mean = np.mean(dataMat, axis=0)

    # decentralization
    feature_decentralized = dataMat - feature_mean

    # calculate the covariance
    # set each column representing a variable, while the rows contain observations.
    cov_mat = np.cov(feature_decentralized, rowvar=False)

    # calculate the eigenvalues of the covariance matrix and the corresponding eigenvectors
    eig_vals, eig_vects = np.linalg.eig(np.mat(cov_mat))

    # descend the eigenvalues
    eig_val_id = np.argsort(eig_vals)
    eig_val_id = eig_val_id[:-(topNfeat + 1):-1]

    # extract the corresponding eigenvectors
    red_eig_vects = eig_vects[:, eig_val_id]

    # descend the dimensions
    low_data_mat = feature_decentralized * red_eig_vects

    return low_data_mat.real, feature_mean.real


filename = '/home/ipb38admin/yuanli/Create_Dataset/features-fullimages.txt'
features = {}
valid_num = 0
feature_matrix = [[]]*2212
feature_sigma = []
with open(filename, 'r') as file_to_read:
    # plt.subplot(211)
    while True:
        lines = file_to_read.readline()
        if not lines:
            break

        try:
            # E_tmp = [float(i) for i in lines.split(" ")]
            E_tmp = [float(i) for i in lines.split()]
            # print(E_tmp)
            # features[p_tmp] = E_tmp
            feature_matrix[valid_num] = E_tmp
            valid_num += 1
            # feature_sigma.append(E_tmp)
            # plt.plot(p_tmp, E_tmp, 'ro', label="point")
        except:
            pass

feature_idex = np.array(feature_matrix)[:, 0]
feature_matrix = np.array(feature_matrix)[:, 1:len(feature_matrix[0])-1]

low_data_mat, feature_mean = pca(feature_matrix)

distances_to_mean_withpca = []
distances_to_mean_withoutpca = []
distances_to_mean_withteaching = []


# choose pictures for mean feature calculation
if 1:
    selected_images = []
    i_select = 0
    cv2.namedWindow('teaching')
    cv2.createButton('yes', input_yes)
    cv2.createButton('no', pass_image)
    while i_select < 20:
        img_path = "/home/ipb38admin/yuanli/Create_Dataset/car/" + str(i_select)
        try:
            img = cv2.imread(img_path)
            img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
            cv2.imshow('teaching', img)
        except:
            array = np.ndarray((120, 500, 3), np.uint8)
            array[:, :, 0] = 0
            array[:, :, 1] = 0
            array[:, :, 2] = 100
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(array, "image wrong!", (10, 50),
                        font, 1, (255, 255, 255), 1)
            cv2.imshow('teaching', array)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break

    cv2.destroyAllWindows()

    selected_feature_mean = np.mean(selected_images, axis=0)

ax = plt.subplot(111, projection='3d')

for i in range(0, len(low_data_mat)):
    ax.scatter(low_data_mat[i, 0], low_data_mat[i, 1], low_data_mat[i, 2], c='r')
    distances_to_mean_withpca.append(calEuclideanDistance(low_data_mat[i], [0, 0, 0]))

for i in range(0, len(low_data_mat)):
    distances_to_mean_withoutpca.append(calEuclideanDistance(feature_matrix[i], feature_mean))

print(feature_mean)

for i in range(0, len(low_data_mat)):
    distances_to_mean_withteaching.append(calEuclideanDistance(feature_matrix[i], selected_feature_mean))

# draw the distributions of all features
if 1:
    # draw the PCA graph
    ax.set_zlabel('Z')
    ax.set_ylabel('Y')
    ax.set_xlabel('X')
    ax.scatter(0, 0, 0, c='b')
    print("Draw the map")

# sort with pca
distances_to_mean_withpca = np.row_stack((distances_to_mean_withpca, feature_idex))
distances_to_mean_withpca = distances_to_mean_withpca.transpose()
distances_to_mean_withpca = distances_to_mean_withpca.tolist()
distances_to_mean_withpca.sort(key=take_first, reverse=False)

# sort without pca
distances_to_mean_withoutpca = np.row_stack((distances_to_mean_withoutpca, feature_idex))
distances_to_mean_withoutpca = distances_to_mean_withoutpca.transpose()
distances_to_mean_withoutpca = distances_to_mean_withoutpca.tolist()
distances_to_mean_withoutpca.sort(key=take_first, reverse=False)

# sort with teaching
distances_to_mean_withteaching = np.row_stack((distances_to_mean_withteaching, feature_idex))
distances_to_mean_withteaching = distances_to_mean_withteaching.transpose()
distances_to_mean_withteaching = distances_to_mean_withteaching.tolist()
distances_to_mean_withteaching.sort(key=take_first, reverse=False)


cv2.namedWindow('image_withpca')
cv2.namedWindow('image_withoutpca')
cv2.namedWindow('image_withteaching')
cv2.namedWindow('distance')

# set the range
cv2.createTrackbar('giving_distance', 'distance', 0, len(low_data_mat)-1, nothing)

while True:
    giving_distance = cv2.getTrackbarPos('giving_distance', 'distance')
    array = np.ndarray((300, 500, 3), np.uint8)
    array[:, :, 0] = 0
    array[:, :, 1] = 0
    array[:, :, 2] = 100
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(array, "with_pca: "+str(round(distances_to_mean_withpca[giving_distance][0], 6)), (10, 50), font, 1, (255, 255, 255), 1)
    cv2.putText(array, "without_pca: "+str(round(distances_to_mean_withoutpca[giving_distance][0], 6)), (10, 100), font, 1, (255, 255, 255), 1)
    cv2.putText(array, "withteaching: " + str(round(distances_to_mean_withteaching[giving_distance][0], 6)), (10, 150), font, 1, (255, 255, 255), 1)
    cv2.imshow('distance', array)

    # with pca
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/car/" + str(int(distances_to_mean_withpca[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withpca', img)
    except:
        print("imagewithpca wrong")

    # with out pca
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/car/" + str(int(distances_to_mean_withoutpca[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withoutpca', img)
    except:
        print("imagewithoutpca wrong")


    # with teaching
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/car/" + str(int(distances_to_mean_withteaching[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withteaching', img)
    except:
        print("imagewithteachingwrong")

    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break


# destroy the window
cv2.destroyAllWindows()
plt.show()