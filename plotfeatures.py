#!/usr/bin/python2.7
# coding: utf-8
# Creating dataset for Bonnet
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

filename = '/home/nubot/bonnet/create_dataset/features-onlymean'
features = {}
valid_num = 0
feature_sum = 0
feature_sigma = []
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
            feature_sigma.append(E_tmp)
            plt.plot(p_tmp, E_tmp, 'ro', label="point")
        except:
            pass
# calculate the mean and var of the feature list
feature_mean = feature_sum/valid_num
tmp = [(i-feature_mean)*(i-feature_mean) for i in feature_sigma]
feature_var = np.sum(tmp)/valid_num

# plot the line of the mean value
x = np.arange(0, 3000, 0.1)
feature_mean_array = feature_mean*np.ones(30000)
plt.plot(x, feature_mean_array, "b", linewidth=2.0)

plt.plot(x, feature_mean * np.ones(30000), "b", linewidth=2.0)
plt.plot(x, (feature_mean + 0.005) * np.ones(30000), "b--", linewidth=2.0)
plt.plot(x, (feature_mean - 0.005) * np.ones(30000), "b--", linewidth=2.0)
plt.title("Medians of features", fontsize="large", fontweight="bold")
plt.xlabel("image_number", fontweight="bold")
plt.ylabel("median_value", fontweight="bold")


# plot the distribution
plt.subplot(212)
num_interval_array = []
x_array = []
x_value = np.min(feature_sigma)
lenth_of_interval = (np.max(feature_sigma) - np.min(feature_sigma)) / 30
while x_value < np.max(feature_sigma):
    num_interval = np.extract(np.where(np.extract(np.where(feature_sigma < x_value+lenth_of_interval),
                                                  feature_sigma) > x_value), feature_sigma)
    x_value += lenth_of_interval
    num_interval_array.append(num_interval.size)
    x_array.append(x_value)

plt.plot(x_array, num_interval_array, "r", linewidth=2.0)

plt.plot(feature_mean*np.ones(900), np.arange(0, 900, 1), "b", linewidth=2.0)
plt.plot((feature_mean + 0.005) * np.ones(900), np.arange(0, 900, 1), "b--", linewidth=2.0)
plt.plot((feature_mean - 0.005) * np.ones(900), np.arange(0, 900, 1), "b--", linewidth=2.0)
plt.title("Feature Distribution", fontsize="large", fontweight="bold")
plt.xlabel("median_value", fontweight="bold")
plt.ylabel("number_of_images", fontweight="bold")
plt.show()

#### TEST ####
# a = np.where(feature_sigma > np.float64(feature_mean + 0.005))[-1]
# print a
# b = a.tolist()
# b.append(np.where(feature_sigma < np.float64(feature_mean - 0.005))[-1])
# print b

# delete_list = delete_list.append(np.where(feature_sigma < (feature_mean - 0.005)))
#
# print delete_list
