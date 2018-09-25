#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


class DeleteOutliers:
    '''using features to delete the outliers of the created dataset.
    Input: the path of dataset and feature_file
    Result: all the outliers are deleted
    '''

    def __init__(self, file_path, dataset_path, method='pca'):
        self.file_path = file_path
        self.dataset_path = dataset_path

        self.feature_matrix = [[]] * sum(1 for line in open(file_path))
        self.feature_idex = []
        # self.feature_matrix_pca = []
        # self.feature_matrix_tsne = []

        self.selected_images = []
        # self.selected_images_pca = []
        # self.selected_images_tsne = []
        self.selected_idexes = []

        self.i_select = 0

        self.method = method

    def file_len(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def nothing(self, a):
        pass

    def take_first(self, elem):
        return elem[0]

    def pass_image(self, a, b):
        self.i_select += 1
        pass

    def cal_euclidean_distance(self, vec1, vec2):
        dist = np.sqrt(np.sum(np.square(vec1 - vec2)))
        return dist

    def input_yes(self, a, b):
        print("i_select: ", self.i_select)

        selected_image = self.feature_matrix[self.i_select]
        self.selected_images.append(selected_image)

        # selected_image_pca = self.feature_matrix_pca[i_select]
        # self.selected_images_pca.append(selected_image_pca)
        #
        # selected_image_tsne = self.feature_matrix_tsne[i_select]
        # self.selected_images_tsne.append(selected_image_tsne)

        selected_idex = self.feature_idex[self.i_select]
        self.selected_idexes.append(selected_idex)

        self.i_select += 1

    def pca(self, dataMat, percentage=0.9):
        # dataMat is the raw data
        # percentage is the percentage of eigenvalues, deciding how many dimensions will be kept.
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

        return low_data_mat

    def get_features(self, file_path):
        valid_num = 0
        feature_matrix = [[]] * sum(1 for line in open(file_path))
        with open(self.file_path, 'r') as file_to_read:
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

        feature_idex = np.array(feature_matrix)[:, 0]
        feature_matrix = np.array(feature_matrix)[:, 1:len(feature_matrix[0]) - 1]

        return feature_idex, feature_matrix

    def select_images_formedian(self, feature_idex):
        # choose iamges to culculate the median feature.
        cv2.namedWindow('image selecting')
        cv2.createButton('yes', self.input_yes)
        cv2.createButton('no', self.pass_image)
        while self.i_select < 20:
            img_path = self.dataset_path + str(int(feature_idex[self.i_select]))
            try:
                img = cv2.imread(img_path)
                img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
                cv2.imshow('image selecting', img)
            except:
                array = np.ndarray((120, 500, 3), np.uint8)
                array[:, :, 0] = 0
                array[:, :, 1] = 0
                array[:, :, 2] = 100
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(array, "image wrong!", (10, 50),
                            font, 1, (255, 255, 255), 1)
                cv2.imshow('image selecting', array)

            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break

        cv2.destroyAllWindows()

    def cal_dis_tomedian(self, feature_matrix, selected_images):
        distances_to_mean = []
        selected_feature_median = np.median(selected_images, axis=0)

        for i in range(0, len(feature_matrix)):
            distances_to_mean.append(
                self.cal_euclidean_distance(feature_matrix[i], selected_feature_median))

        return distances_to_mean, selected_feature_median

    def draw_distribution(self, feature_matrix, selected_feature_median, method='pca'):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(0, len(feature_matrix)):
            if self.feature_idex[i] < 89:
                ax.scatter(feature_matrix[i, 0], feature_matrix[i, 1], c='r')
            else:
                ax.scatter(feature_matrix[i, 0], feature_matrix[i, 1], c='b')
        ax.scatter(selected_feature_median[0], selected_feature_median[1], c='g', marker='*')

        # draw the graph
        ax.set_ylabel('dimention 2')
        ax.set_xlabel('dimention 1')
        if method is 'pca':
            ax.set_title('feature distributions with pca')
        elif method is 'tsne':
            ax.set_title('feature distributions with tsne')
        else:
            ax.set_title('feature distributions')

        fig.show()
        plt.pause(0)
    
    def decide_threshold(self, method='tsne', draw_distribution=True):

        feature_idex, feature_matrix = self.get_features(self.file_path)

        self.feature_matrix = feature_matrix
        self.feature_idex = feature_idex

        self.select_images_formedian(feature_idex)
        
        if method is 'pca':
            print("use PCA.")
            feature_matrix_pca = self.pca(feature_matrix, percentage=0.9)
            selected_images_pca = []

            for vaule in self.selected_idexes:
                selected_images_pca.append(feature_matrix_pca[np.where(feature_idex == vaule)])

            distances_to_mean, selected_feature_median = \
                self.cal_dis_tomedian(feature_matrix_pca, selected_images_pca)

            # sort with pca
            distances_to_mean = np.row_stack((distances_to_mean, feature_idex))
            distances_to_mean = distances_to_mean.transpose()
            distances_to_mean = distances_to_mean.tolist()
            distances_to_mean.sort(key=self.take_first, reverse=False)

            cv2.namedWindow('Using PCA')

        elif method is 'tsne':
            print("use TSNE.")
            feature_matrix_tsne = TSNE(learning_rate=100, init='pca').fit_transform(feature_matrix)
            selected_images_tsne = []

            for vaule in self.selected_idexes:
                selected_images_tsne.append(feature_matrix_tsne[np.where(feature_idex == vaule)])

            distances_to_mean, selected_feature_median = \
                self.cal_dis_tomedian(feature_matrix_tsne, selected_images_tsne)

            # sort with tsne
            distances_to_mean = np.row_stack((distances_to_mean, feature_idex))
            distances_to_mean = distances_to_mean.transpose()
            distances_to_mean = distances_to_mean.tolist()
            distances_to_mean.sort(key=self.take_first, reverse=False)

            cv2.namedWindow('Using TSNE')
        
        else:
            print("only use selected images.")
            distances_to_mean, selected_feature_median = self.cal_dis_tomedian(feature_matrix, self.selected_images)
            # sort with teaching
            distances_to_mean = np.row_stack((distances_to_mean, feature_idex))
            distances_to_mean = distances_to_mean.transpose()
            distances_to_mean = distances_to_mean.tolist()
            distances_to_mean.sort(key=self.take_first, reverse=False)

            cv2.namedWindow('Only selecting')
        
        # set the range
        cv2.namedWindow('distance')
        cv2.createTrackbar('giving_distance', 'distance', 0, len(feature_matrix) - 1, self.nothing)

        while True:
            giving_distance = cv2.getTrackbarPos('giving_distance', 'distance')
            array = np.ndarray((100, 500, 3), np.uint8)
            array[:, :, 0] = 0
            array[:, :, 1] = 0
            array[:, :, 2] = 100
            font = cv2.FONT_HERSHEY_SIMPLEX

            if method is 'pca':
                cv2.putText(array, "Using PCA: " + str(round(distances_to_mean[giving_distance][0], 6)),
                            (10, 50), font, 1, (255, 255, 255), 1)

                img_path = self.dataset_path + str(int(distances_to_mean[giving_distance][1]))
                try:
                    img = cv2.imread(img_path)
                    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
                    cv2.imshow('Using PCA', img)
                except:
                    print("image Using PCA wrong")

            elif method is 'tsne':
                cv2.putText(array, "Using TSNE: " + str(round(distances_to_mean[giving_distance][0], 6)),
                            (10, 50), font, 1, (255, 255, 255), 1)

                img_path = self.dataset_path + str(int(distances_to_mean[giving_distance][1]))
                try:
                    img = cv2.imread(img_path)
                    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
                    cv2.imshow('Using TSNE', img)
                except:
                    print("image Using TSNE wrong")

            else:
                cv2.putText(array, "Only selecting: " + str(round(distances_to_mean[giving_distance][0], 6)),
                            (10, 50), font, 1, (255, 255, 255), 1)


                img_path = self.dataset_path + str(int(distances_to_mean[giving_distance][1]))
                try:
                    img = cv2.imread(img_path)
                    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
                    cv2.imshow('Only selecting', img)
                except:
                    print("image wrong")

            cv2.imshow('distance', array)

            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
        
        # destroy the window
        cv2.destroyAllWindows()

        if draw_distribution:
            if method is 'pca':
                self.draw_distribution(feature_matrix_pca, np.squeeze(selected_feature_median), method)
            elif method is 'tsne':
                self.draw_distribution(feature_matrix_tsne, np.squeeze(selected_feature_median), method)
            else:
                self.draw_distribution(feature_matrix, np.squeeze(selected_feature_median), method)


# for test
if __name__ == '__main__':
    file_path = "/home/ipb38admin/yuanli/Create_Dataset/features.txt"
    dataset_path = "/home/ipb38admin/yuanli/Create_Dataset/cat/"  # need a '/' at the end of the path
    # method = 'pac'
    search = DeleteOutliers(file_path, dataset_path)
    search.decide_threshold()
