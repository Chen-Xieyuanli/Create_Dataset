#!/usr/bin/python2.7
# coding: utf-8
# CreateDataset for Bonnet

import time  # Importing the time library to check the time of code execution
import os
import argparse
from ruamel.yaml import YAML  # for comments
# from google_images_download import google_images_download
from google_images_crawler import GoogleImages
from baidu_images_crawler import BaiduImages


class CreateDataset:
    '''create dataset for Bonnet.
    Input: keywords
    Output: Dataset including downloaded images regarding keywords and the related yaml file
    Error:
        1. may use proxy to connect google;
        2. Google allows us to scrape the images page out of the box with 100 images in there.
        If we want more than 100 images, we need selenium (with chromedriver) to automatically
        scroll down page and get more images.
    TODO: download more images
    '''

    def __init__(self):
        pass

    def user_input(self):
        parser = argparse.ArgumentParser("./our_crawler_1.py")
        parser.add_argument(
            '--keywords',
            type=str,
            required=True,
            help='Keywords for searching'
        )
        parser.add_argument(
            '--proxy',
            type=str,
            required=False,
            help='using proxy'
        )
        parser.add_argument(
            '--y_name',
            type=str,
            required=False,
            help='name: "general"'
        )
        parser.add_argument(
            '--y_data_dir',
            type=str,
            required=False,
            help='data_dir: "/cache/datasets/persons/dataset"'
        )
        parser.add_argument(
            '--y_buff',
            type=int,
            required=False,
            help='buff: True'
        )
        parser.add_argument(
            '--y_buff_nr',
            type=int,
            required=False,
            help='buff_nr: 3000'
        )
        parser.add_argument(
            '--y_img_prop_width',
            type=int,
            required=False,
            help='width: 512'
        )
        parser.add_argument(
            '--y_img_prop_height',
            type=int,
            required=False,
            help='height: 512'
        )
        parser.add_argument(
            '--y_img_prop_depth',
            type=int,
            required=False,
            help='depth: 3'
        )
        parser.add_argument(
            '--y_force_resize',
            type=bool,
            required=False,
            help='force_resize: True'
        )
        parser.add_argument(
            '--y_force_remap',
            type=bool,
            required=False,
            help='force_remap: False'
        )
        parser.add_argument(
            '--y_label_map',
            type=str,
            required=False,
            help='label_map: 0: "background", 1: "person"'
        )
        parser.add_argument(
            '--y_color_map',
            type=str,
            required=False,
            help='color_map: 0: [0, 0, 0], 1: [0, 255, 0]'
        )
        parser.add_argument(
            '--y_label_remap',
            type=str,
            required=False,
            help='label_remap: 0: 0 1: 1'
        )
        parser.add_argument(
            '--y_directory',
            type=str,
            required=False,
            help='create the yaml file in a specific directory'
        )
        parser.add_argument(
            '--y_filename',
            type=str,
            required=False,
            help='create the yaml file using a specific name'
        )
        FLAGS, unparsed = parser.parse_known_args()

        # try to get the keywords
        try:
            if (FLAGS.keywords):
                print("get keywords: ", FLAGS.keywords)
        except:
            print("Error getting keywords...")
            quit()

        args = parser.parse_args()
        arguments = vars(args)
        records = []
        records.append(arguments)
        return records

    def deafault_yaml(self):
        deafault_yaml = """\
        # dataset cfg file
            name: "general"
            data_dir: "/cache/datasets/persons/dataset"
            buff: True            # if this is true we buffer buff_n images in a fifo
            buff_nr: 3000         # number of images to keep in fifo (prefetch batch) <-should be bigger than batch size to make sense
            img_prop:
              width: 512
              height: 512
              depth: 3            # number of channels in original image
            force_resize: True    # if dataset contains images of different size, it should be True
            force_remap: False
            label_map:
              0: "background"
            color_map: # bgr
              0: [0, 0, 0]
            label_remap:          # for softmax (it must be an index of the onehot array)
              0: 0
            """
        return deafault_yaml

    def set_yaml_parameters(self, arguments, dataset):
        if arguments['y_name']:
            dataset['name'] = arguments['y_name']
        if arguments['y_data_dir']:
            dataset['data_dir'] = arguments['y_data_dir']
        if arguments['y_buff']:
            dataset['buff'] = arguments['y_buff']
        if arguments['y_buff_nr']:
            dataset['buff_nr'] = arguments['y_buff_nr']
        if arguments['y_img_prop_width']:
            dataset['img_prop']['width'] = arguments['y_img_prop_width']
        if arguments['y_img_prop_height']:
            dataset['img_prop']['height'] = arguments['y_img_prop_height']
        if arguments['y_img_prop_depth']:
            dataset['img_prop']['depth'] = arguments['y_img_prop_depth']
        if arguments['y_force_resize']:
            dataset['force_resize'] = arguments['y_force_resize']
        if arguments['y_force_remap']:
            dataset['force_remap'] = arguments['y_force_remap']
        if arguments['y_label_map']:
            dataset['label_map'] = arguments['y_label_map']
        if arguments['y_color_map']:
            dataset['color_map'] = arguments['y_color_map']
        if arguments['y_label_remap']:
            dataset['label_remap'] = arguments['y_label_remap']

    def set_maps(self, arguments, paths, dataset):
        # automatically generate the direction of the dataset
        key_num = 0  # count for keys
        label_num = 0  # count for labels
        color_num_1 = 0  # count for colormap
        color_num_2 = 0  # count for colormap
        color_num_3 = 0  # count for colormap

        # for each key create a yaml unit.
        for keys in paths:
            # automatically generate the data_dir for each label
            lists = list(paths[keys])

            # try to find downloaded picture
            try:
                raw_dir = lists[0]
            except:
                print("Error downloading images...")

            if not arguments['y_data_dir']:
                dataset['data_dir'] = os.path.dirname(os.path.dirname(raw_dir))
            raw_data_dir = os.path.dirname(raw_dir)
            print("data_dir:", raw_data_dir)
            filename = 'label' + str(key_num)
            data_dir = "data_dir" + str(key_num)
            dataset[filename] = keys
            dataset[data_dir] = raw_data_dir

            # automatically generate the relative maps
            if not arguments['y_label_map']:
                dataset['label_map'][label_num] = keys
            if not arguments['y_color_map']:
                dataset['color_map'][label_num] = [
                    color_num_1, color_num_2, color_num_3]
                if color_num_1 < 192:
                    color_num_1 += 64
                elif color_num_2 < 192:
                    color_num_2 += 64
                elif color_num_3 < 192:
                    color_num_3 += 64
                else:
                    print("Color Map Overflow!!!")
            if not arguments['y_label_remap']:
                dataset['label_remap'][label_num] = key_num
            key_num += 1
            label_num += 20

    def decide_directory(self, arguments):
        # decide folder name
        if arguments['y_directory']:
            folder = arguments['y_directory']  # use the specific direction
        else:
            folder = 'cfg/'  # default direction
        if not os.path.exists(folder):
            os.makedirs(folder)

        # decide filename name
        if arguments['y_filename']:
            filename = arguments['y_filename']  # use the specific direction
        else:
            filename = 'dataset'  # default direction

        # decide directory
        directory = folder + filename
        return directory

    def crawl_images(self, arguments):
        # download multiple images based on keywords/keyphrase download
        # using google crawler
        # class instantiation
        # response1 = google_images_download.googleimagesdownload()

        # wrapping response in a variable just for consistency
        # paths contains the maps from keywords to all its images
        # arguments["chromedriver"] = "/home/nubot/bonnet/create_dataset/chromedriver"
        # arguments["limit"] = 2000
        # paths = response1.download(arguments)
        response1 = GoogleImages(arguments["keywords"])
        paths, download_count = response1.download()

        # using baidu crawler
        # class instantiation
        response2 = BaiduImages(arguments["keywords"], download_count = download_count)
        response2.download()

        return paths

    def create_yaml_file(self, arguments, paths):
        yaml = YAML()
        dataset = yaml.load(self.deafault_yaml())

        # Set the parameters in yaml
        self.set_yaml_parameters(arguments, dataset)

        # Set the dataset maps
        self.set_maps(arguments, paths, dataset)

        # decide_directory
        directory = self.decide_directory(arguments)
        yaml_file = open(directory + '.yaml', 'wb+')
        yaml.dump(dataset, yaml_file)
        yaml_file.close()
        return

    def create_dataset(self):
        records = self.user_input()

        # start the timer
        t0 = time.time()
        for arguments in records:
            # crawl images
            paths = self.crawl_images(arguments)
            print("\nEverything downloaded!")

            # create the relative yaml file
            self.create_yaml_file(arguments, paths)
            print("\nYaml files created!")

        # stop the timer
        t1 = time.time()

        # Calculating the total time required to crawl
        total_time = t1 - t0
        print("Total time taken: " + str(total_time) + " Seconds")
        pass


# for test
if __name__ == '__main__':
    response = CreateDataset()
    response.create_dataset()
