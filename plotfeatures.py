#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet
import os
import sys
# import cv
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def nothing(x):
    pass

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


filename = '/home/xieyuanli-chen/bonnet/create_dataset/features.txt'
features = {}
valid_num = 0
feature_matrix = [[]]*2660
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
            # print E_tmp
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
print(feature_mean)
print(len(low_data_mat))
distances_to_mean_withpca = []
distances_to_mean_withoutpca = []
ax = plt.subplot(111, projection='3d')
for i in range(0, len(low_data_mat)):
    ax.scatter(low_data_mat[i, 0], low_data_mat[i, 1], low_data_mat[i, 2], c='r')
    distances_to_mean_withpca.append(calEuclideanDistance(low_data_mat[i], [0, 0, 0]))

for i in range(0, len(low_data_mat)):
    distances_to_mean_withoutpca.append(calEuclideanDistance(feature_matrix[i], feature_mean))

# sort with pca
distances_to_mean_withpca = np.row_stack((distances_to_mean_withpca, feature_idex))
distances_to_mean_withpca = distances_to_mean_withpca.transpose()
distances_to_mean_withpca = distances_to_mean_withpca.tolist()
distances_to_mean_withpca.sort(key=take_first, reverse=False)

# sor without pca
distances_to_mean_withoutpca = np.row_stack((distances_to_mean_withoutpca, feature_idex))
distances_to_mean_withoutpca = distances_to_mean_withoutpca.transpose()
distances_to_mean_withoutpca = distances_to_mean_withoutpca.tolist()
distances_to_mean_withoutpca.sort(key=take_first, reverse=False)

if 0:
    # draw the PCA graph
    ax.set_zlabel('Z')
    ax.set_ylabel('Y')
    ax.set_xlabel('X')
    ax.scatter(0, 0, 0, c='b')
    plt.show()

cv2.namedWindow('image_withpca')
cv2.namedWindow('image_withoutpca')
cv2.namedWindow('distance')
# set the range
cv2.createTrackbar('giving_distance', 'distance', 0, len(low_data_mat), nothing)

while True:
    giving_distance = cv2.getTrackbarPos('giving_distance', 'distance')
    array = np.ndarray((120, 500, 3), np.uint8)
    array[:, :, 0] = 0
    array[:, :, 1] = 0
    array[:, :, 2] = 100
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(array, "with_pca: "+str(round(distances_to_mean_withpca[giving_distance][0], 6)), (10, 50), font, 1, (255, 255, 255), 1)
    cv2.putText(array, "without_pca: "+str(round(distances_to_mean_withoutpca[giving_distance][0], 6)), (10, 100), font, 1, (255, 255, 255), 1)
    cv2.imshow('distance', array)

    # with pca
    img_path = "/home/xieyuanli-chen/bonnet/create_dataset/cat/" + str(int(distances_to_mean_withpca[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withpca', img)
    except:
        print("image wrong")

    # with out pca
    img_path = "/home/xieyuanli-chen/bonnet/create_dataset/cat/" + str(int(distances_to_mean_withoutpca[giving_distance][1]))
    try:
        img = cv2.imread(img_path)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image_withoutpca', img)
    except:
        print("image wrong")

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

# destroy the window
cv2.destroyAllWindows()