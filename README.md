# Create_Dataset
create dataset for Bonnet

# How to run
```sh
$ python create_dataset.py --keywords "bears"
```

# version control
## version 3
### version 3.1
- **changes**: 1. Set the storing directory using the given folder name and the keyword instead of slicing from the path of downloaded images; 2. Solved the wrong number of downloaded images problem; 3. Solved the bug of using proxy.
- **bugs**: 1. cannot reach the expected number of images; 2. some of the downloaded images are unreadable; 3. downloading speed is still very slow.
### version 3.0
- **status**: At this version, We could download about thousands of images from both google and baidu.
- **changes**: Add google_images_crawler.py and chromedriver.
- **TODO**: The download speed is very low, which might be solved by using multiple threads.
## version 2
- **status**: At this version, We could download about 100 images from google and 2000 images from baidu.
- **changes**: Add baidu_images_crawler.py
- **TODO**: 1. Create google_images_crawler.py to solve the limited download number problem; 2. Add more search engine.
## version 1
- **status**: At this version, We could download about 100 images from google.
