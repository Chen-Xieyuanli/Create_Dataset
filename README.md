# The new version is transfered into gitlab. For more information please send email to xieyuanli.chen@uni-bonn.de

# Create_Dataset
## Second step
Clean the outliers of the created dataset.

### How to run a demo
```sh
$ python clean_outliers.py path/to/the/Dataset
```

### Version Control
#### Version 2
- **Status**: At this version, We extract the last-layer features of each images and calculate the medium valve of them. Using these mediums, we estimate the distribution of the features and clean the outliers by setting the confidence interval.
- **TODO**: Combining the step one and step two.
#### Version 1
- **Status**: At this version, We use the pretrained ResNet with Pytorch to classify each image in the created dataset and keep the class number of each image.
- **TODO**: Using the class numbers, we would like to find out and delete the outliers.
Classification result
![image](https://github.com/Chen-Xieyuanli/Create_Dataset/blob/master/Medians_and_distribution.png)


## First step
Automatically download images from Google, Bing and Baidu and create dataset for Bonnet.

### How to run
```sh
$ python create_dataset.py --keywords "bears"
```

### Version Control
#### Version 4
- **Status**: At this version, We could download about three thousand images from Google Bing and Baidu. Due to the copyright issues, that's all we could download from these three websites using one keyword. 
- **Changes**: 
1. Added bing_images_crawler.py; 
2. Solved the bug of the unreadable images; 
3. Used multi-threads to solve the problem of the slow downloading speed;
- **Bugs**: The number of images corresponding to one keyword is limited. We could solve this problem by automaticlly adding prefixs or suffixs, e.g. "bear"->"white bear", to double the quantity. 
- **TODO**: Solve the bug and test the created dataset in Bonnet.
  
#### Version 3
##### Version 3.1
- **Changes**: 
1. Set the storing directory using the given folder name and the keyword instead of slicing from the path of downloaded images; 
2. Solved the wrong number of downloaded images problem; 
3. Solved the bug of using proxy.
- **Bugs**: 
1. Cannot reach the expected number of images; 
2. Some of the downloaded images are unreadable; 
3. The downloading speed is still very slow.
##### Version 3.0
- **Status**: At this version, We could download about thousands of images from both google and baidu.
- **Changes**: Added google_images_crawler.py and chromedriver.
- **TODO**: The download speed is very low, which might be solved by using multiple threads.
#### Version 2
- **Status**: At this version, We could download about 100 images from google and 2000 images from baidu.
- **Changes**: Added baidu_images_crawler.py
- **TODO**: 1. Create google_images_crawler.py to solve the limited download number problem; 2. Add more search engine.
#### Version 1
- **Status**: At this version, We could download about 100 images from google.

