.. :changelog:

Release History
---------------

0.4.5 (2017-11-14)
++++++++++++++++++

**Features**

- rename multi product search to discover search


0.4.4 (2017-10-27)
++++++++++++++++++

**Features**

- support multi product search

0.4.3 (2016-11-08)
++++++++++++++++++

**Improvement**

- add "X-Requested-With" in the request header when calling api

0.4.1 (2016-09-28)
++++++++++++++++++

**Improvement**

- fix the issue for recommendation endpoint and add a test cases

0.4.0 (2016-09-20)
++++++++++++++++++

**Features**

- add recommendation endpoint

0.3.9 (2016-07-20)
++++++++++++++++++

**Improvement**

- allow passing search endpoint as parameter

0.3.8 (2016-04-20)
++++++++++++++++++

**Improvement**

- exclude im_url from the required fields in update

0.3.7 (2016-01-21)
++++++++++++++++++

**Improvement**

- add missing info in multipart upload

0.3.6 (2015-12-24)
++++++++++++++++++

**Improvement**

- send raw image in uploadsearch to make consistent results as in dashboard

0.3.5 (2015-12-24)
++++++++++++++++++

**Bug fix**

- fix tests due to httpretty incompatibility for python 3

0.3.4 (2015-12-24)
++++++++++++++++++

**Bug fix**

- encode url parameter in uploadsearch

0.3.3 (2015-12-04)
++++++++++++++++++

**Bug fix**

- fix dict iteritem issue for python 3

0.3.2 (2015-12-04)
++++++++++++++++++

**Improvement**

- support arbitrary parameters in search

0.3.0 (2015-11-13)
++++++++++++++++++

**Improvement**

- Add get_all_fl field so that user can query for all metafields

0.2.8 (2015-11-12)
++++++++++++++++++

**Improvement**

- support arbitrary parameters in insert

0.2.6 (2015-07-30)
++++++++++++++++++

**Bugfixes**

- update insert_status with extra parameters

0.2.4 (2015-06-08)
++++++++++++++++++

**Bugfixes**

- Drop support for python 2.6

0.2.2 (2015-06-08)
++++++++++++++++++

**Bugfixes**

- Separate POST request data/parameters

0.2.0 (2015-04-10)
++++++++++++++++++

**Bugfixes**

- Close opened files in tearDown()

**Features and Improvements**

- Test compatibility on py26, py34

0.1.0 (2015-04-06)
---------------------

* First release on PyPI.
