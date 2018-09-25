#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet
import os
import sys
# import cv
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
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

    selected_image_pca = feature_matrix_pca[i_select]
    selected_images_pca.append(selected_image_pca)

    selected_image_tsne = feature_matrix_tsne[i_select]
    selected_images_tsne.append(selected_image_tsne)

    selected_idex = feature_idex[i_select]
    selected_idexes.append(selected_idex)
    i_select += 1


def take_first(elem):
    return elem[0]

def calEuclideanDistance(vec1,vec2):
    dist = np.sqrt(np.sum(np.square(vec1 - vec2)))
    return dist

def pca(dataMat, percentage=0.9):
        # calculate the mean value of each column
        feature_mean = np.mean(dataMat, axis=0)

        # decentralization
        feature_decentralized = dataMat - feature_mean

        # calculate the covariance
        # set each column representing a variable, while the rows contain observations.
        cov_mat = np.cov(feature_decentralized, rowvar=False)

        # calculate the eigenvalues of the covariance matrix and the corresponding eigenvectors
        eig_vals, eig_vects = np.linalg.eigh(cov_mat)

        # descend the eigenvalues
        eig_val_id = np.argsort(eig_vals)[::-1]

        # calculate the percentage of eigenvalues
        eig_vals_sum = np.sum(eig_vals)
        temp_sum = 0
        best_dimention = 0
        for id in eig_val_id:
            temp_sum += eig_vals[id]
            best_dimention += 1
            if temp_sum >= eig_vals_sum * percentage:
                break

        eig_val_id_ = eig_val_id[0:best_dimention]

        # extract the corresponding eigenvectors
        red_eig_vects = eig_vects[:, eig_val_id_]

        # descend the dimensions
        low_data_mat = feature_decentralized.dot(red_eig_vects)

        return low_data_mat, feature_mean


filename = '/home/ipb38admin/yuanli/Create_Dataset/features_cat_tennis.txt'
features = {}
valid_num = 0
feature_matrix = [[]]*99
feature_sigma = []
with open(filename, 'r') as file_to_read:
    while True:
        lines = file_to_read.readline()
        if not lines:
            break

        try:
            E_tmp = [float(i) for i in lines.split()]
            feature_matrix[valid_num] = E_tmp
            valid_num += 1

        except:
            pass
feature_idex = np.array(feature_matrix)[:, 0]  # take care of the size of feature_matrix
feature_matrix = np.array(feature_matrix)[:, 1:len(feature_matrix[0])-1]
feature_matrix_tsne = TSNE(learning_rate=100, init='pca').fit_transform(feature_matrix)
feature_matrix_pca, feature_mean = pca(feature_matrix)

distances_to_mean_withpca = []
distances_to_mean_withoutpca = []
distances_to_mean_withteaching = []
distances_to_mean_withtsne = []


# choose pictures for mean feature calculation
if 1:
    selected_images = []
    selected_images_pca = []
    selected_images_tsne = []
    selected_idexes = []
    i_select = 0
    cv2.namedWindow('teaching')
    cv2.createButton('yes', input_yes)
    cv2.createButton('no', pass_image)
    while i_select < 20:
        img_path = "/home/ipb38admin/yuanli/Create_Dataset/cat_tennis/" + str(int(feature_idex[i_select]))
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
    selected_feature_mean_tsne = np.mean(selected_images_tsne, axis=0)
    selected_feature_mean_pca = np.mean(selected_images_pca, axis=0)

    selected_feature_median = np.median(selected_images, axis=0)
    selected_feature_median_tsne = np.median(selected_images_tsne, axis=0)
    selected_feature_median_pca = np.median(selected_images_pca, axis=0)


ax_pca = plt.subplot(121)

# len(feature_matrix) == len(feature_matrix_pca) == len(feature_matrix_tsne)
for i in range(0, len(feature_matrix_pca)):
    if feature_idex[i] < 89:
        ax_pca.scatter(feature_matrix_pca[i, 0], feature_matrix_pca[i, 1], c='r')
    else:
        ax_pca.scatter(feature_matrix_pca[i, 0], feature_matrix_pca[i, 1], c='b')

    ax_pca.scatter(selected_feature_median_pca[0], selected_feature_median_pca[1], c='g', marker='*')
    ax_pca.scatter(selected_feature_mean_pca[0], selected_feature_mean_pca[1], c='y', marker='s')
    distances_to_mean_withpca.append(calEuclideanDistance(feature_matrix_pca[i], selected_feature_mean_pca))

for i in range(0, len(feature_matrix_pca)):
    distances_to_mean_withoutpca.append(calEuclideanDistance(feature_matrix[i], feature_mean))

for i in range(0, len(feature_matrix_pca)):
    distances_to_mean_withteaching.append(calEuclideanDistance(feature_matrix[i], selected_feature_mean))

for i in range(0, len(feature_matrix_pca)):
    distances_to_mean_withtsne.append(calEuclideanDistance(feature_matrix_tsne[i], selected_feature_mean_tsne))

# draw the distributions of all features
if 1:
    # draw the PCA graph
    # ax_pca.set_zlabel('Z')
    ax_pca.set_ylabel('Y')
    ax_pca.set_xlabel('X')
    ax_pca.set_title('PCA graph')
    # ax_pca.scatter(0, 0, c='b')
    print("Draw the map 1")

ax_tsne = plt.subplot(122)
for i in range(0, len(feature_matrix_pca)):

    # Number changes according to the given dataset
    if feature_idex[i] < 89:
        ax_tsne.scatter(feature_matrix_tsne[i, 0], feature_matrix_tsne[i, 1], c='r')
    else:
        ax_tsne.scatter(feature_matrix_tsne[i, 0], feature_matrix_tsne[i, 1], c='b')

    ax_tsne.scatter(selected_feature_median_tsne[0], selected_feature_median_tsne[1], c='g', marker='*')
    ax_tsne.scatter(selected_feature_mean_tsne[0], selected_feature_mean_tsne[1], c='y', marker='s')

# draw the distributions of all features
if 1:
    # draw the PCA graph
    ax_tsne.set_ylabel('Y')
    ax_tsne.set_xlabel('X')
    ax_tsne.set_title('TSNE graph')
    # ax_tsen.scatter(0, 0, c='b')
    print("Draw the map 2")

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

# sort with tsne
distances_to_mean_withtsne = np.row_stack((distances_to_mean_withtsne, feature_idex))
distances_to_mean_withtsne = distances_to_mean_withtsne.transpose()
distances_to_mean_withtsne = distances_to_mean_withtsne.tolist()
distances_to_mean_withtsne.sort(key=take_first, reverse=False)


cv2.namedWindow('image_withpca')
cv2.namedWindow('image_withoutpca')
cv2.namedWindow('image_withteaching')
cv2.namedWindow('image_withtsne')
cv2.namedWindow('distance')

# set the range
cv2.createTrackbar('giving_distance', 'distance', 0, len(feature_matrix_pca) - 1, nothing)

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
    cv2.putText(array, "withtsne: " + str(round(distances_to_mean_withtsne[giving_distance][0], 6)), (10, 200), font, 1, (255, 255, 255), 1)
    cv2.imshow('distance', array)

    # with pca
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/cat_tennis/" + str(int(distances_to_mean_withpca[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withpca', img)
    except:
        print("imagewithpca wrong")

    # with out pca
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/cat_tennis/" + str(int(distances_to_mean_withoutpca[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withoutpca', img)
    except:
        print("imagewithoutpca wrong")


    # with teaching
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/cat_tennis/" + str(int(distances_to_mean_withteaching[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withteaching', img)
    except:
        print("imagewithteachingwrong")


    # with tsne
    img_path = "/home/ipb38admin/yuanli/Create_Dataset/cat_tennis/" + str(int(distances_to_mean_withtsne[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withtsne', img)
    except:
        print("imagewithtsnewrong")

    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break


# destroy the window
cv2.destroyAllWindows()
plt.show()