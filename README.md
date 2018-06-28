# Create_Dataset
create dataset for Bonnet

# How to run
```sh
$ python create_dataset.py --keywords "bears"
```

# version control
## version 3.0
- **status**: At this version, We could download about thousands of images from both google and baidu.
- **changes**: Add google_images_crawler.py and chromedriver.
- **TODO**: The download speed is very low, which might be solved by using multiple threads.
## version 2.0
- **status**: At this version, We could download about 100 images from google and 2000 images from baidu.
- **changes**: Add baidu_images_crawler.py
- **TODO**: 1. Create google_images_crawler.py to solve the limited download number problem; 2. Add more search engine.
## version 1.0
- **status**: At this version, We could download about 100 images from google.
