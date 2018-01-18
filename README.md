# ViSearch Python SDK

[<img src="https://travis-ci.org/visenze/visearch-sdk-python.svg">](https://travis-ci.org/visenze/visearch-sdk-python) [<img src="https://img.shields.io/pypi/v/visearch.svg">](https://pypi.python.org/pypi/visearch) [![CodeFactor](https://www.codefactor.io/repository/github/visenze/visearch-sdk-python/badge)](https://www.codefactor.io/repository/github/visenze/visearch-sdk-python)

----
## Table of Contents
 1. [Overview](#1-overview)
 2. [Setup](#2-setup)
 3. [Initialization](#3-initialization)
 4. [Indexing Images](#4-indexing-images)
      - 4.1 [Indexing Your First Images](#41-indexing-your-first-images)
      - 4.2 [Image with Metadata](#42-image-with-metadata)
      - 4.3 [Updating Images](#43-updating-images)
      - 4.4 [Removing Images](#44-removing-images)
      - 4.5 [Check Indexing Status](#44-check-indexing-status)
 5. [Solution APIs](#5-solution-apis)
      - 5.1 [Visually Similar Recommendations](#51-visually-similar-recommendations)
      - 5.2 [Search by Image](#52-search-by-image)
        - 5.2.1 [Selection Box](#521-selection-box)
        - 5.2.2 [Resizing Settings](#522-resizing-settings)
      - 5.3 [Search by Color](#53-search-by-color)
      - 5.4 [Multiproduct Search](#54-multiproduct-search)
 6. [Search Results](#6-search-results)
 7. [Advanced Search Parameters](#7-advanced-search-parameters)
      - 7.1 [Retrieving Metadata](#71-retrieving-metadata)
      - 7.2 [Filtering Results](#72-filtering-results)
      - 7.3 [Result Score](#73-result-score)
      - 7.4 [Automatic Object Recognition Beta](#74-automatic-object-recognition-beta)
 8. [Declaration](#8-declaration)


----

## 1. Overview
ViSearch is an API that provides accurate, reliable and scalable image search. ViSearch API provides endpoints that let developers index their images and perform image searches efficiently. ViSearch API can be easily integrated into your web and mobile applications. More details about ViSearch API can be found in the [documentation](http://www.visenze.com/docs/overview/introduction).

The ViSearch Python SDK is an open source software for easy integration of ViSearch Search API with your application server. It provides three search methods based on the ViSearch Search API - pre-indexed search, color search and upload search. The ViSearch Python SDK also provides an easy integration of the ViSearch Data API which includes data inserting and data removing. For source code and references, visit the github [repository](https://github.com/visenze/visearch-sdk-python).

* Supported on Python 2.7+ and 3.3+
 
## 2. Setup
To install visearch, simply:

```
$ pip install visearch
```

To upgrade visearch to latest version, simply:

```
$ pip install -U visearch
```

##3. Initialization
To start using ViSearch API, initialize ViSearch client with your ViSearch API credentials. Your credentials can be found in [ViSearch Dashboard](https://dashboard.visenze.com):

```python
from visearch import client

access_key = 'your app access key'
secret_key = 'your app secret key'

api = client.ViSearchAPI(access_key, secret_key)
```

## 4. Indexing Images


### 4.1 Indexing Your First Images

Built for scalability, ViSearch API enables fast and accurate searches on high volume of images. Before making your first image search, you need to prepare a list of images and index them into ViSearch by calling the /insert endpoint. Each image must have a unique identifier and a publicly downloadable URL. ViSearch will parallelly fetch your images from the given URLs, and index the downloaded for searching. After the image indexes are built, you can start searching for [similar images using the unique identifier](https://github.com/visenze/visearch-sdk-python/blob/master/README_md.md#51-pre-indexed-search), [using a color](https://github.com/visenze/visearch-sdk-python/blob/master/README_md.md#52-color-search), or [using another image](https://github.com/visenze/visearch-sdk-python/blob/master/README_md.md#53-upload-search).

To index your images, prepare a list of images and call the /insert endpoint. 

```python
# the list of images to be indexed
# the unique identifier of the image 'im_name', the publicly downloadable url of the image 'im_url'
images = [
    {'im_name': 'red_dress', 'im_url': 'http://mydomain.com/images/red_dress.jpg'},
    {'im_name': 'blue_dress', 'im_url': 'http://mydomain.com/images/blue_dress.jpg'}
]
# calls the /insert endpoint to index the image
response = api.insert(images)
```

 > Each ```insert``` call to ViSearch accepts a maximum of 100 images. We recommend indexing your images in batches of 100 for optimized image indexing speed.

### 4.2 Image with Metadata

Images usually come with descriptive text or numeric values as metadata, for example:
title, description, category, brand, and price of an online shop listing image
caption, tags, geo-coordinates of a photo.

ViSearch combines the power of text search with image search. You can index your images with metadata, and leverage text based query and filtering for even more accurate image search results, for example:
limit results within a price range
limit results to certain tags, and some keywords in the captions
For detailed reference for result filtering, see [Advanced Search Parameters](https://github.com/visenze/visearch-sdk-python/blob/master/README_md.md#7-advanced-search-parameters).

To index your images with metadata, first you need to configure the metadata schema in [ViSearch Dashboard](https://dashboard.visenze.com). You can add and remove metadata keys, and modify the metadata types to suit your needs.

Let's assume you have the following metadata schema configured:

| Name | Type | Searchable |
| ---- | ---- | ---------- |
| title | string | true |
| description | text | true |
| price | float | true |

Then index your image with title, decription, and price:

```python
images = [{
           'im_name': 'blue_dress', 
           'im_url': 'http://mydomain.com/images/blue_dress.jpg',
           'title': 'Blue Dress',
           'description': 'A blue dress',
           'price': 100.0
          },
          ... 
         ]
# calls the /insert endpoint to index the image
response = api.insert(images)
```
Metadata keys are case-sensitive, and metadata without a matching key in the schema will not be processed by ViSearch. Make sure to configure metadata schema for all of your metadata keys.

### 4.3 Updating Images

If you need to update an image or its metadata, call the ```insert``` endpoint with the same unique identifier of the image. ViSearch will fetch the image from the updated URL and index the new image, and replace the metadata of the image if provided.

```python
images = [{
           'im_name': 'blue_dress', 
           'im_url': 'http://mydomain.com/images/blue_dress.jpg',
           'title': 'Blue Dress',
           'description': 'A blue dress',
           'price': 100.0
          },
          ... 
         ]
# calls the /update endpoint to index the image
response = api.update(images)
```

 > Each ```insert``` call to ViSearch accepts a maximum of 100 images. We recommend updating your images in batches of 100 for optimized image indexing speed.

### 4.4 Removing Images

In case you decide to remove some of the indexed images, you can call the /remove endpoint with the list of unique identifier of the indexed images. ViSearch will then remove the specified images from the index. You will not be able to perform pre-indexed search on this image, and the image will not be found in any search result.

```python
image_names = ["red_dress", "blue_dress"]
response = api.remove(image_names)
```

> We recommend calling ```remove``` in batches of 100 images for optimized image indexing speed.


## 4.5 Check Indexing Status

The fetching and indexing process take time, and you may only search for images after their indexs are built. If you want to keep track of this process, you can call the insert_status endpoint with the image's transaction identifier.

```python
import time
import math

# the list of images to be indexed
# the unique identifier of the image 'im_name', the publicly downloadable url of the image 'im_url'
images = [
    {'im_name': 'pic5', 'im_url': 'http://mydomain.com/images/vintage_wingtips.jpg'},
]

response = api.insert(images)

trans_id = response['trans_id']

percent = 0
while (percent < 100):
    time.sleep(1)

    status_response = api.insert_status(trans_id)
    if 'result' in status_response and len(status_response['result']) > 0:
        percent = status_response['result'][0]['processed_percent']
        print '{}% complete'.format(percent)

page_index = 1
error_per_page = 10
fail_count = None
status_response = api.insert_status(trans_id, page_index, error_per_page)
if 'result' in status_response and len(status_response['result']) > 0:
    result_data = status_response['result'][0]
    print result_data
    fail_count = result_data['fail_count']
    print 'Start time: {}'.format(result_data['start_time'])
    print 'Update time: {}'.format(result_data['update_time'])
    print "{} insertions with {} succeed and {} fail".format(
        result_data['total'],
        result_data['success_count'],
        result_data['fail_count']
        )

if fail_count > 0:
    result_data = status_response['result'][0]
    error_limit = result_data['error_limit']
    total_page_number = int(math.ceil(float(fail_count) / error_limit))
    for i in range(total_page_number):
        page_index = i + 1
        status_response = api.insert_status(trans_id, page_index, error_per_page)
        error_list = status_response['result'][0]['error_list']
        for error in error_list:
            print "failure at page {} with error message {}".format(
                page_index,
                error)
```


## 5. Solution APIs

### 5.1 Visually Similar Recommendations
**Visually Similar Recommendations** solution is to search for visually similar images in the image database giving an indexed image’s unique identifier (im_name).

```python
response = api.search("blue_dress")
```

### 5.2 Search by Image
**Search by image** solution is to search similar images by uploading an image or providing an image url.

* Using an image from a local file path:

```python
image_path = 'blue_dress.jpg'
response = api.uploadsearch(image_path=image_path)
```

* Using image url:

```python
image_url = 'http://mydomain.com/images/red_dress.jpg'
response = api.uploadsearch(image_url=image_url)
```

#### 5.2.1 Selection Box

If the object you wish to search for takes up only a small portion of your image, or other irrelevant objects exists in the same image, chances are the search result could become inaccurate. Use the Box parameter to refine the search area of the image to improve accuracy. Noted that the box coordinated is setted with respect to the original size of the image passed, it will be automatically scaled to fit the resized image for uploading:

```python
image_url = 'http://mydomain.com/images/red_dress.jpg'
box = (0,0,10,10)
response = api.uploadsearch(image_url=image_url, box=box)
```

#### 5.2.2 Resizing Settings

When performing upload search, you might experience increasing search latency with increasing image file sizes. This is due to the increased time transferring your images to the ViSearch server, and the increased time for processing larger image files in ViSearch.

By default, the `uploadsearch` api will upload the raw image. But to reduce upload search latency, the `uploadsearch` api supports dimension reduction, which is specified using the `resize` parameter

If your image dimensions exceed 512 pixels, the STANDARD resize settings will resize the copy to dimensions not exceeding 512x512 pixels. This is the optimized size to lower search latency while not sacrificing search accuracy for general use cases:

```python
# client.uploadSearch(params) is equivalent to using STANDARD resize settings, 512x512 and jpeg 75 quality
image_path = 'blue_dress.jpg'
response = api.uploadsearch(image_path=image_path, resize='STANDARD')
```

If your image contains fine details such as textile patterns and textures, use the HIGH resize settings to get better search results:

```python
# for images with fine details, use HIGH resize settings 1024x1024 and jpeg 75 quality
image_path = 'blue_dress.jpg'
response = api.uploadsearch(image_path=image_path, resize='HIGH')
```

Or provide customized resize settings:

```python
# using customized resize settings 800x800 and jpeg 80 quality
image_path = 'blue_dress.jpg'
response = api.uploadsearch(image_path=image_path, resize=(800, 800, 80))
```


### 5.3 Search by Color
**Search by color** solution is to search images with similar color by providing a color code. The color code should be in Hexadecimal and passed to the colorsearch service.

```python
response = api.colorsearch("fa4d4d")
```

### 5.4 Multiproduct Search
**Mulproduct search**  is for detecting all products and return similar products for each. For a query image, detect all the objects existed in the image and search for similar products for each of them.

```python
response = api.discoversearch(im_url='http://www.test.com/test.jpg', detection='all', detection_limit=3,
                              result_limit=10, detection_sensitivity='high', box=(0, 0, 10, 10)) 
```

| Name | Example | Default | Description |
| ---- | ------- | ------- | ----------- |
| im_url | "http://www.test.com/test.jpg" | None | The url for the image to be downloaded and searched against the image database. User must input one of the following: image file, im\_url or im\_id. |
| im_id | "abcd1234" | None | For each uploaded image ViSearch service will return an unique im_id which can be used to do further search without downloading the image again. User must input one of the following: image file, im\_url or im\_id.
| image | "/home/ubuntu/test.jpg" | None | The image file object that will be searched against the image database. User must input one of the following: image file, im\_url or im\_id.
| detection | "eyewear" | "all" | The type of objects to be recognized in the query image, can be used in following ways <ul> <li> detection = {algorithm supported object type}, recognize objects of the particular type user specified. </li> <li> detection = all, recognize all the possible types of objects. </li> <li> detection = null, recognize all the possible types of objects. </li> <li> detection = “ “, turn off detection, use the whole image to search. </li> <li> detection = anything other than the supported product type , turn off detection, use the whole image to search. </li> </ul>
| detection_limit | 7 | 5 | Maximum number of products could be detected for a given image, default value is 5, Maximum value is 30. <br> Return the objects with higher confidence score first.
| detection_sensitivity | "high" | "low" | Parameter to set the detection to more or less sensitive. Default is low. <ul><li>detection\_sensitivity=low, less sensitive detection, will only return objects that are very confident. </li> <li>detection\_sensitivity=high, more sensitive detection, will return as many objects as possible.</li></ul>
| result_limit | 15 | 10 | The number of results returned per page for each product. <br> Default value is 10, Maximum value is 100.
| box | (0, 0, 10, 10) | None | Optional parameter for restricting the image area x1,y1,x2,y2.

## 6. Search Results

ViSearch returns a maximum number of 1000 most relevant image search results. You can provide pagination parameters to control the paging of the image search results.

Pagination parameters:

| Name | Type | Description |
| ---- | ---- | ----------- |
| page | Integer | Optional parameter to specify the page of results. The first page of result is 1. Defaults to 1. |
| limit | Integer | Optional parameter to specify the result per page limit. Defaults to 10. |

```python
page = 1
limit = 25
response = api.uploadsearch(image_url=image_url, page=page, limit=limit)
```


## 7. Advanced Search Parameters

### 7.1 Retrieving Metadata

To retrieve metadata of your image results, provide the list (or tuple) of metadata keys for the metadata value to be returned in the `fl` (field list) property:

```python
fl = ["price", "brand", "title", "im_url"]  #, or fl = ("price", "brand", "title", "im_url")
response = api.uploadsearch(image_url=image_url, fl=fl)
```

To retrieve all metadata of your image results, specify ```get_all_fl``` parameter and set it to ```True```:

```python
get_all_fl = True
response = api.uploadsearch(image_url=image_url, get_all_fl=get_all_fl)
```

 > Only metadata of type string, int, and float can be retrieved from ViSearch. Metadata of type text is not available for retrieval.

### 7.2 Filtering Results

To filter search results based on metadata values, provide a dict of metadata key to filter value in the `fq` (filter query) property:

```python
fq = {"im_cate": "bags", "price": "10,199"}
response = api.uploadsearch(image_url=image_url, fq=fq)
```

Querying syntax for each metadata type is listed in the following table:

Type | FQ
--- | ---
string | Metadata value must be exactly matched with the query value, e.g. "Vintage Wingtips" would not match "vintage wingtips" or "vintage"
text | Metadata value will be indexed using full-text-search engine and supports fuzzy text matching, e.g. "A pair of high quality leather wingtips" would match any word in the phrase
int | Metadata value can be either: <ul><li>exactly matched with the query value</li><li>matched with a ranged query ```minValue,maxValue```, e.g. int value ```1, 99```, and ```199``` would match ranged query ```0,199``` but would not match ranged query ```200,300```</li></ul>
float | Metadata value can be either <ul><li>exactly matched with the query value</li><li>matched with a ranged query ```minValue,maxValue```, e.g. float value ```1.0, 99.99```, and ```199.99``` would match ranged query ```0.0,199.99``` but would not match ranged query 200.0,300.0</li></ul>

### 7.3 Result Score

ViSearch image search results are ranked in descending order i.e. from the highest scores to the lowest, ranging from 1.0 to 0.0. By default, the score for each image result is not returned. You can turn on the **boolean** ```score``` property to retrieve the scores for each image result:

```python
score = True
response = api.uploadsearch(image_url=image_url, score=score)
```

If you need to restrict search results from a minimum score to a maximum score, specify the ```score_min``` and/or ```score_max``` parameters:

Name | Type | Description
---- | ---- | -----------
score_min | Float | Minimum score for the image results. Default is 0.0.
score_max | Float | Maximum score for the image results. Default is 1.0.

```python
score_min = 0.5
score_max = 0.8
response = api.uploadsearch(image_url=image_url, score_max=score_max, score_min=score_min)
```

### 7.4 Automatic Object Recognition Beta
With Automatic Object Recognition, ViSearch /uploadsearch API is smart to detect the objects present in the query image and suggest the best matched product type to run the search on. 

You can turn on the feature in upload search by setting the API parameter "detection=all". We are now able to detect various types of fashion items, including `Top`, `Dress`, `Bottom`, `Shoe`, `Bag`, `Watch` and `Indian Ethnic Wear`. The list is ever-expanding as we explore this feature for other categories. 

Notice: This feature is currently available for fashion application type only. You will need to make sure your app type is configurated as "fashion" on [ViSenze dashboard](https://developers.visenze.com/setup/#Choose-Your-Application-Type). 

```python
param = {'detection': 'all'}
response = api.uploadsearch(image_url=image_url, **param)
```

You could also recognize objects from a paticular type on the uploaded query image through configuring the detection parameter to a specific product type as "detection={type}". Our API will run the search within that product type.

Sample request to detect `bag` in an uploaded image:

```python
param = {'detection': 'bag'}
response = api.uploadsearch(image_url=image_url, **param)
```

The detected product types are listed in `product_types` together with the match score and box area of the detected object. Multiple objects can be detected from the query image and they are ranked from the highest score to lowest. The full list of supported product types by our API will also be returned in `product_types_list`. 

## 8. Declaration
* The image upload.jpg included in the SDK is downloaded from http://pixabay.com/en/boots-shoes-pants-folded-fashion-690502/
