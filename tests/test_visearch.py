#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import httpretty
import json
import re
import sys
import os.path
from six.moves.urllib.parse import unquote
from visearch import client
from visearch.bind import ViSearchAPIError, ViSearchClientError


def request_callback(request, uri, headers):
    request_callback.request = request
    mock_status, mock_resp = active_mock_response
    return (mock_status, headers, mock_resp)


active_mock_response = None


class TestVisearch(unittest.TestCase):
    """
        test the logic on the sdk client side
    """

    def setUp(self):
        super(TestVisearch, self).setUp()
        self.access_key = 'debug'
        self.secret_key = 'debug'
        self.api = client.ViSearchAPI(self.access_key, self.secret_key)

        self.fixture_dir = 'tests/fixtures/'
        self.image_fp = open(os.path.join(self.fixture_dir, 'images.json'))
        self.image_path = os.path.dirname(os.path.realpath(__file__)) + '/fixtures/upload.jpg'
        images = json.load(self.image_fp)
        self.inserted_images = images['inserted_images']
        self.query_image = images['query_image']

        self.insert_entpoint = "http://visearch.visenze.com/insert"
        self.remove_entpoint = "http://visearch.visenze.com/remove"
        self.insert_status_rootendpoint = "http://visearch.visenze.com/insert/status/"
        self.idsearch_entpoint = "http://visearch.visenze.com/search"
        self.recommendation_entpoint = "http://visearch.visenze.com/recommendation"
        self.colorsearch_entpoint = "http://visearch.visenze.com/colorsearch"
        self.uploadsearch_entpoint = "http://visearch.visenze.com/uploadsearch"
        self.discoversearch_entpoint = "http://visearch.visenze.com/discoversearch"

    def tearDown(self):
        self.image_fp.close()

    @httpretty.activate
    def test_auth_info(self):
        global active_mock_response

        active_mock_response = (200, '{"status": "OK", "total": 10, "method": "insert", "trans_id": 352649805417295872}')

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        self.api.insert(self.inserted_images)

        from requests.auth import _basic_auth_str
        expected_auth_str = _basic_auth_str(self.access_key, self.secret_key)
        self.assertEqual(request_callback.request.headers['authorization'], expected_auth_str)

    @httpretty.activate
    def test_headers(self):
        global active_mock_response

        active_mock_response = (200, '{"status": "OK", "total": 10, "method": "insert", "trans_id": 352649805417295872}')

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        self.api.insert(self.inserted_images)
        self.assertTrue('x-requested-with' in request_callback.request.headers)
        self.assertTrue(request_callback.request.headers['x-requested-with'].startswith('ViSenze-Python-SDK'))

    @httpretty.activate
    def test_auth_invalid(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "insert", "limit": 0, "result": [], "error": ["Invalid access key or secret key."], "total": 0, "page": 0}'

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        resp = self.api.insert(self.inserted_images)

        self.assertEqual(resp['error'], ['Invalid access key or secret key.'])

    def _build_parsed_body(self, body):
        parsed_body = unquote(body.decode('utf-8')).split('&')
        parsed_body = dict([(item.split('=')[0], [item.split('=')[1]]) for item in parsed_body])
        return parsed_body

    @httpretty.activate
    def test_insert_requestparams(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "total": 10, "method": "insert", "trans_id": 352649805417295872}'

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        self.api.insert(self.inserted_images)

        self.assertEqual(request_callback.request.method, 'POST')
        expected_images_count = len(self.inserted_images) * len(self.inserted_images[0])

        request_callback.request.parsed_body = self._build_parsed_body(request_callback.request.body)

        images_count_in_query = len(request_callback.request.parsed_body)
        self.assertEqual(images_count_in_query, expected_images_count)

        attr_names = set()
        for item in request_callback.request.parsed_body.keys():
            attrname_index_list = re.findall(r'(\w+)\[(\d+)\]', item)
            self.assertEqual(len(attrname_index_list), 1)
            attr_name = attrname_index_list[0][0]
            attr_names.add(attr_name)
        self.assertEqual(attr_names, set(self.inserted_images[0].keys()))

    @httpretty.activate
    def test_insert_noimage(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "total": 0, "method": "insert", "trans_id": 352977401971617792, "error": [{"error_message": "No image inserted.", "error_code": 104}]}'

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        resp = self.api.insert([])

        self.assertEqual(request_callback.request.parsed_body, '')
        self.assertEqual(resp['error'][0]['error_code'], 104)

    @httpretty.activate
    def test_insert_breakmaxinum(self):
        global active_mock_response

        active_mock_response = 502, '{}'

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        insert_images = []
        for i in range(100):
            for image in self.inserted_images:
                insert_images.append({
                    'im_name': image['im_name'] + str(i),
                    'im_url': image['im_url']
                })
        self.assertRaises(ViSearchAPIError, self.api.insert, insert_images)

    @httpretty.activate
    def test_insert_singleimage(self):
        global active_mock_response

        active_mock_response = 200, '{}'

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        image = self.inserted_images[0]
        self.api.insert(image)

        request_callback.request.parsed_body = self._build_parsed_body(request_callback.request.body)

        self.assertEqual(len(request_callback.request.parsed_body), len(image))

    @httpretty.activate
    def test_insert_invlaidimagename(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "total": 0, "method": "insert", "trans_id": 353021306532409344, "error": [{"index": 0, "im_name": "not valid name", "error_code": 107, "error_message": "Invalid im_name."}]}'

        httpretty.register_uri(httpretty.POST, self.insert_entpoint, body=request_callback)

        image = self.inserted_images[0]
        image['im_name'] = 'not valid name'
        resp = self.api.insert(image)

        self.assertEqual(resp['error'][0]['error_code'], 107)

    @httpretty.activate
    def test_remove_noimage(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "total": 0, "method": "remove"}'

        httpretty.register_uri(httpretty.POST, self.remove_entpoint, body=request_callback)

        resp = self.api.remove([])

        self.assertEqual(request_callback.request.parsed_body, '')
        self.assertEqual(resp['total'], 0)

    @httpretty.activate
    def test_remove_singleimage(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "total": 0, "method": "remove"}'

        httpretty.register_uri(httpretty.POST, self.remove_entpoint, body=request_callback)

        resp = self.api.remove([])

        self.assertEqual(request_callback.request.parsed_body, '')
        self.assertEqual(resp['total'], 0)

    @httpretty.activate
    def test_remove_non_exists_singleimage(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "warning", "total": 0, "method": "remove", "error": [{"im_name": "nonexistsimagename", "error_code": 102, "error_message": "Image not found with im_name."}]}'

        httpretty.register_uri(httpretty.POST, self.remove_entpoint, body=request_callback)

        image_name = 'nonexistsimagename'
        resp = self.api.remove(image_name)

        request_callback.request.parsed_body = self._build_parsed_body(request_callback.request.body)

        self.assertTrue('im_name[0]' in request_callback.request.parsed_body)
        self.assertTrue(image_name == request_callback.request.parsed_body['im_name[0]'][0])
        self.assertEqual(resp['error'][0]['error_code'], 102)

    @httpretty.activate
    def test_remove_non_exists_multipleimages(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "warning", "total": 1, "method": "remove", "error": [{"im_name": "b", "error_code": 102, "error_message": "Image not found with im_name."}, {"im_name": "a", "error_code": 102, "error_message": "Image not found with im_name."}]}'

        httpretty.register_uri(httpretty.POST, self.remove_entpoint, body=request_callback)

        non_exists_imagenames = ['a', 'b']
        image_names = [self.inserted_images[0]['im_name'], ] + non_exists_imagenames
        resp = self.api.remove(image_names)

        request_callback.request.parsed_body = self._build_parsed_body(request_callback.request.body)

        query_images = [query_image_name for query_image_val in request_callback.request.parsed_body.values() for query_image_name in query_image_val]

        self.assertEqual(set(image_names), set(query_images))
        for item in request_callback.request.querystring.keys():
            attrname_index_list = re.findall(r'(\w+)\[(\d+)\]', item)
            self.assertEqual(len(attrname_index_list), 1)
        self.assertEqual(len(resp['error']), len(non_exists_imagenames))

    @httpretty.activate
    def test_insert_status_invalid_trans_id(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "insert/status", "error": [{"error_message": "Transaction not found with trans_id.", "error_code": 101}]}'

        invalid_trans_id = '123'
        httpretty.register_uri(httpretty.GET, self.insert_status_rootendpoint + invalid_trans_id, body=request_callback)

        resp = self.api.insert_status(invalid_trans_id)

        self.assertEqual(request_callback.request.path.split('/')[-1], invalid_trans_id)
        self.assertEqual(request_callback.request.querystring, {})
        self.assertEqual(resp['error'][0]['error_code'], 101)

    @httpretty.activate
    def test_insert_status_valid_trans_id(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "insert/status", "result": [{"update_time": "2015-04-07T10:02:51.048+0000", "start_time": "2015-04-07T10:02:51.048+0000", "processed_percent": 100, "fail_count": 0, "success_count": 10, "total": 10, "trans_id": 352649805417295872}]}'

        invalid_trans_id = '352649805417295872'
        httpretty.register_uri(httpretty.GET, self.insert_status_rootendpoint + invalid_trans_id, body=request_callback)

        resp = self.api.insert_status(invalid_trans_id)

        self.assertEqual(request_callback.request.path.split('/')[-1], invalid_trans_id)
        self.assertEqual(request_callback.request.querystring, {})
        self.assertEqual(resp['status'], "OK")

    @httpretty.activate
    def test_idsearch_valid_im_name(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162"}, {"im_name": "19609426340"}, {"im_name": "40623053246"}, {"im_name": "25301792601"}, {"im_name": "19356394967"}, {"im_name": "38213377507"}, {"im_name": "38475333633"}, {"im_name": "41229714662"}, {"im_name": "42894441677"}], "error": [], "total": 9, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        resp = self.api.search(im_name)
        self.assertTrue('im_name' in request_callback.request.querystring.keys())
        self.assertEqual(im_name, request_callback.request.querystring['im_name'][0])
        self.assertEqual(resp['status'], 'OK')

    @httpretty.activate
    def test_recommendation_valid_im_name(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162"}, {"im_name": "19609426340"}, {"im_name": "40623053246"}, {"im_name": "25301792601"}, {"im_name": "19356394967"}, {"im_name": "38213377507"}, {"im_name": "38475333633"}, {"im_name": "41229714662"}, {"im_name": "42894441677"}], "error": [], "total": 9, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.recommendation_entpoint, body=request_callback)

        im_name = '39012157235'
        resp = self.api.recommendation(im_name)
        self.assertTrue('im_name' in request_callback.request.querystring.keys())
        self.assertEqual(im_name, request_callback.request.querystring['im_name'][0])
        self.assertEqual(resp['status'], 'OK')

    @httpretty.activate
    def test_idsearch_invalid_im_name(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "search", "limit": 0, "result": [], "error": ["im_name is invalid."], "total": 0, "page": 0}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = 'invalid image name'
        resp = self.api.search(im_name)
        self.assertEqual(im_name, request_callback.request.querystring['im_name'][0])
        self.assertEqual(resp['status'], 'fail')
        self.assertEqual(resp['error'][0], 'im_name is invalid.')

    @httpretty.activate
    def test_idsearch_nonexists_im_name(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "search", "limit": 30, "result": [], "error": ["Image not found with im_name."], "total": 0, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = 'notexistsname'
        resp = self.api.search(im_name)
        self.assertEqual(im_name, request_callback.request.querystring['im_name'][0])
        self.assertEqual(resp['status'], 'fail')
        self.assertEqual(resp['error'][0], 'Image not found with im_name.')

    @httpretty.activate
    def test_colorsearch_validcolor(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "colorsearch", "limit": 30, "result": [{"im_name": "25301792601"}, {"im_name": "40623053246"}, {"im_name": "38475333633"}, {"im_name": "41229714662"}, {"im_name": "39882808162"}, {"im_name": "19356394967"}, {"im_name": "19609426340"}, {"im_name": "39012157235"}, {"im_name": "38213377507"}, {"im_name": "42894441677"}], "error": [], "total": 10, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.colorsearch_entpoint, body=request_callback)

        color = 'ffffff'
        resp = self.api.colorsearch(color)
        self.assertTrue('color' in request_callback.request.querystring.keys())
        self.assertEqual(color, request_callback.request.querystring['color'][0])
        self.assertEqual(resp['status'], 'OK')

    @httpretty.activate
    def test_colorsearch_invalidcolor(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "colorsearch", "limit": 0, "result": [], "error": ["color is invalid."], "total": 0, "page": 0}'

        httpretty.register_uri(httpretty.GET, self.colorsearch_entpoint, body=request_callback)

        color = 'ffffff000'
        resp = self.api.colorsearch(color)

        self.assertTrue('color' in request_callback.request.querystring.keys())
        self.assertEqual(color, request_callback.request.querystring['color'][0])
        self.assertEqual(resp['status'], 'fail')

    @httpretty.activate
    def test_fileuploadsearch_valid(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "uploadsearch", "limit": 30, "result": [{"im_name": "19609426340"}, {"im_name": "40623053246"}, {"im_name": "41229714662"}, {"im_name": "19356394967"}, {"im_name": "39882808162"}, {"im_name": "25301792601"}, {"im_name": "38213377507"}, {"im_name": "42894441677"}, {"im_name": "38475333633"}, {"im_name": "39012157235"}], "error": [], "total": 10, "page": 1}'

        httpretty.register_uri(httpretty.POST, self.uploadsearch_entpoint, body=request_callback)

        image_path = 'tests/fixtures/upload.jpg'
        resp = self.api.uploadsearch(image_path=image_path)

        self.assertEqual(request_callback.request.method, 'POST')
        if (sys.version_info > (3, 0)):
            content_type = dict(request_callback.request.headers._headers)['Content-Type'].split(';')[0].strip()
        else:
            content_type = request_callback.request.headers.__dict__['type']
        self.assertEqual(content_type, 'multipart/form-data')
        self.assertEqual(resp['status'], 'OK')

    def test_fileuploadsearch_filenotexist(self):
        image_path = 'nonexists.jpg'
        self.assertRaises(IOError, self.api.uploadsearch, image_path=image_path)

    def test_fileuploadsearch_fileformatnotvalid(self):
        image_path = 'tests/fixtures/notimage.pdf'
        self.assertRaises(IOError, self.api.uploadsearch, image_path=image_path, resize='HIGH')

    @httpretty.activate
    def test_urluploadsearch_valid(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "uploadsearch", "limit": 30, "result": [{"im_name": "19609426340"}, {"im_name": "40623053246"}, {"im_name": "39882808162"}, {"im_name": "19356394967"}, {"im_name": "39012157235"}, {"im_name": "25301792601"}, {"im_name": "41229714662"}, {"im_name": "38475333633"}, {"im_name": "38213377507"}, {"im_name": "42894441677"}], "error": [], "total": 10, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.uploadsearch_entpoint, body=request_callback)

        image_url = 'http://gw3.alicdn.com/bao/uploaded/i4/TB12.BQHXXXXXX_XpXXXXXXXXXX_!!0-item_pic.jpg'
        resp = self.api.uploadsearch(image_url=image_url)
        self.assertEqual(request_callback.request.method, 'GET')
        self.assertEqual(request_callback.request.querystring['im_url'][0], image_url)
        self.assertEqual(resp['status'], 'OK')

    @httpretty.activate
    def test_urluploadsearch_get_all_fl(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "uploadsearch", "limit": 30, "result": [{"im_name": "147562129", "value_map": {"detect": "top", "group_id": "175066446", "im_url": "http://ak2.polyvoreimg.com/cgi/img-thing/size/y/tid/147562129.jpg", "key_word": ""}}], "error": [], "total": 1, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.uploadsearch_entpoint, body=request_callback)

        image_url = 'http://gw3.alicdn.com/bao/uploaded/i4/TB12.BQHXXXXXX_XpXXXXXXXXXX_!!0-item_pic.jpg'
        resp = self.api.uploadsearch(image_url=image_url, get_all_fl=True)
        self.assertEqual(request_callback.request.method, 'GET')
        self.assertEqual('key_word' in resp['result'][0]['value_map'], True)
        self.assertEqual(resp['status'], 'OK')

    @httpretty.activate
    def test_urluploadsearch_urlnotvalid(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "uploadsearch", "limit": 0, "result": [], "error": ["Invalid image or im_url."], "total": 0, "page": 0}'

        httpretty.register_uri(httpretty.GET, self.uploadsearch_entpoint, body=request_callback)

        image_url = 'http://example.com/docs/fake.jpg'
        resp = self.api.uploadsearch(image_url=image_url)
        self.assertEqual(request_callback.request.method, 'GET')
        self.assertEqual(request_callback.request.querystring['im_url'][0], image_url)
        self.assertEqual(resp['status'], 'fail')

    @httpretty.activate
    def test_search_box_valid(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "uploadsearch", "limit": 30, "result": [{"im_name": "38213377507"}, {"im_name": "39012157235"}, {"im_name": "19356394967"}, {"im_name": "41229714662"}, {"im_name": "19609426340"}, {"im_name": "39882808162"}, {"im_name": "40623053246"}, {"im_name": "42894441677"}, {"im_name": "38475333633"}, {"im_name": "25301792601"}], "error": [], "total": 10, "page": 1}'

        httpretty.register_uri(httpretty.POST, self.uploadsearch_entpoint, body=request_callback)

        image_path = 'tests/fixtures/upload.jpg'
        box = [0, 0, 10, 10]
        resp = self.api.uploadsearch(image_path=image_path, box=box)

        self.assertEqual(request_callback.request.querystring['box'][0], ','.join(map(str, box)))
        self.assertEqual(resp['status'], 'OK')

    def test_search_box_notwellformatted(self):
        image_path = 'tests/fixtures/upload.jpg'
        box = [0, 0, 10]
        self.assertRaises(ViSearchClientError, self.api.uploadsearch, image_path=image_path, box=box)

    @httpretty.activate
    def test_search_resize_valid(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "uploadsearch", "limit": 30, "result": [{"im_name": "38213377507"}, {"im_name": "39012157235"}, {"im_name": "19356394967"}, {"im_name": "41229714662"}, {"im_name": "39882808162"}, {"im_name": "40623053246"}, {"im_name": "19609426340"}, {"im_name": "42894441677"}, {"im_name": "38475333633"}, {"im_name": "25301792601"}], "error": [], "total": 10, "page": 1}'

        httpretty.register_uri(httpretty.POST, self.uploadsearch_entpoint, body=request_callback)

        image_path = 'tests/fixtures/upload.jpg'
        resize = (100, 100, 90)
        resp = self.api.uploadsearch(image_path=image_path, resize=resize)
        self.assertEqual(resp['status'], 'OK')

    def test_search_resize_invalid(self):
        image_path = 'tests/fixtures/upload.jpg'
        resize = (100, 100)
        self.assertRaises(ViSearchClientError, self.api.uploadsearch, image_path=image_path, resize=resize)

    @httpretty.activate
    def test_search_pagination(self):
        global active_mock_response

        active_mock_response = 200, '{}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        page = 10
        limit = 100
        self.api.search(im_name, page=page, limit=limit)
        self.assertEqual(request_callback.request.querystring['page'][0], str(page))
        self.assertEqual(request_callback.request.querystring['limit'][0], str(limit))

    @httpretty.activate
    def test_search_metadata_validfl(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162", "value_map": {"category": "162402", "price": "125.000000"}}, {"im_name": "19609426340", "value_map": {"category": "162402", "price": "136.000000"}}, {"im_name": "40623053246", "value_map": {"category": "162402", "price": "159.000000"}}, {"im_name": "25301792601", "value_map": {"category": "162104", "price": "24.000000"}}, {"im_name": "19356394967", "value_map": {"category": "50011130", "price": "195.000000"}}, {"im_name": "38213377507", "value_map": {"category": "50011130", "price": "285.000000"}}, {"im_name": "38475333633", "value_map": {"category": "162401", "price": "79.000000"}}, {"im_name": "41229714662", "value_map": {"category": "162402", "price": "119.000000"}}, {"im_name": "42894441677", "value_map": {"category": "50012906", "price": "94.050003"}}], "error": [], "total": 9, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        fl = ['price', 'category']
        self.api.search(im_name, fl=fl)

        self.assertEqual(request_callback.request.querystring['fl'], fl)

    @httpretty.activate
    def test_search_metadata_nonexistfl(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162", "value_map": {"price": "125.000000"}}, {"im_name": "19609426340", "value_map": {"price": "136.000000"}}, {"im_name": "40623053246", "value_map": {"price": "159.000000"}}, {"im_name": "25301792601", "value_map": {"price": "24.000000"}}, {"im_name": "19356394967", "value_map": {"price": "195.000000"}}, {"im_name": "38213377507", "value_map": {"price": "285.000000"}}, {"im_name": "38475333633", "value_map": {"price": "79.000000"}}, {"im_name": "41229714662", "value_map": {"price": "119.000000"}}, {"im_name": "42894441677", "value_map": {"price": "94.050003"}}], "error": [], "total": 9, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        fl = ['price', 'nonexistsattr']
        self.api.search(im_name, fl=fl)

        self.assertEqual(request_callback.request.querystring['fl'], fl)

    @httpretty.activate
    def test_search_filtering_fq(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162"}, {"im_name": "41229714662"}], "error": [], "total": 2, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        fq = {'price': '100,130', 'category': '162402'}
        self.api.search(im_name, fq=fq)

        self.assertEqual(request_callback.request.querystring['fq'], ['{0}:{1}'.format(k, v) for k, v in fq.items()])

    @httpretty.activate
    def test_search_resultscore_valid_scorevalue(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162", "score": 0.5227514505386353}, {"im_name": "19609426340", "score": 0.5115451216697693}, {"im_name": "40623053246", "score": 0.5078160166740417}, {"im_name": "25301792601", "score": 0.48725369572639465}, {"im_name": "19356394967", "score": 0.48042991757392883}, {"im_name": "38213377507", "score": 0.4748014807701111}, {"im_name": "38475333633", "score": 0.4609438478946686}, {"im_name": "41229714662", "score": 0.4512198567390442}, {"im_name": "42894441677", "score": 0.3062390983104706}], "error": [], "total": 9, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        score = True
        self.api.search(im_name, score=score)

        self.assertEqual(request_callback.request.querystring['score'][0], str(score))

    @httpretty.activate
    def test_search_resultscore_invalid_scorevalue(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "search", "limit": 0, "result": [], "error": ["score must be false or true."], "total": 0, "page": 0}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        score = 'nonbool'
        resp = self.api.search(im_name, score=score)

        self.assertEqual(request_callback.request.querystring['score'][0], score)
        self.assertEqual(resp['error'][0], "score must be false or true.")

    @httpretty.activate
    def test_search_resultscore_valid_scorerange(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "search", "limit": 30, "result": [{"im_name": "39882808162"}, {"im_name": "19609426340"}, {"im_name": "40623053246"}, {"im_name": "25301792601"}, {"im_name": "19356394967"}, {"im_name": "38213377507"}, {"im_name": "38475333633"}, {"im_name": "41229714662"}, {"im_name": "42894441677"}], "error": [], "total": 9, "page": 1}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        score_min = 0.2
        score_max = 0.8
        resp = self.api.search(im_name, score_min=score_min, score_max=score_max)

        self.assertEqual(request_callback.request.querystring['score_min'][0], str(score_min))
        self.assertEqual(request_callback.request.querystring['score_max'][0], str(score_max))
        self.assertEqual(resp['status'], "OK")

    @httpretty.activate
    def test_search_resultscore_invalid_scorerange(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "fail", "method": "search", "limit": 0, "result": [], "error": ["score_max must be no more than 1"], "total": 0, "page": 0}'

        httpretty.register_uri(httpretty.GET, self.idsearch_entpoint, body=request_callback)

        im_name = '39012157235'
        score_min = 0.2
        score_max = 1.8
        resp = self.api.search(im_name, score_min=score_min, score_max=score_max)

        self.assertEqual(request_callback.request.querystring['score_min'][0], str(score_min))
        self.assertEqual(request_callback.request.querystring['score_max'][0], str(score_max))
        self.assertEqual(resp['error'][0], "score_max must be no more than 1")

    def get_request_params(self, request):
        body = request.parse_request_body(request.body)

        return body

    @httpretty.activate
    def test_discoversearch_valid_im_url_with_default_values(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "discoversearch", "error": [], "result_limit": 10, "detection_limit": 5, "page": 1, "objects": [{"type": "top", "attributes": {}, "score": 0.697765052318573, "box": [4, 55, 98, 98], "total": 100, "result": [{"im_name": "KOBO_26a8d231-97ea-477f-816b-f0a9b26935c2", "score": 0.6767474412918091}, {"im_name": "KOBO_6eca8321-f392-43f2-ae7d-6bff567f4218", "score": 0.6764472126960754}, {"im_name": "RAKUTEN-GB_rzcd-46621", "score": 0.6700685620307922}, {"im_name": "KOBO_927ef9af-0f45-4c5e-8dc1-fd01c55ab13f", "score": 0.6667808294296265}, {"im_name": "OVERSTOCK_8343843_11708334", "score": 0.6594167947769165}, {"im_name": "OVERSTOCK_8343843_4359899", "score": 0.6594167947769165}, {"im_name": "KOBO_fad3c7c7-c9da-4063-be25-f9f8c6d9f7ce", "score": 0.6584149599075317}, {"im_name": "KOBO_ea343fd9-0a5a-403a-a2e5-71c7f6ef7fa9", "score": 0.6571913957595825}, {"im_name": "KOBO_5b76493a-63ea-4899-8275-da696b5caa22", "score": 0.6553171873092651}, {"im_name": "KOBO_9e525cd1-5b57-4009-a1df-aafb87766087", "score": 0.6512559056282043}]}], "object_types_list": [{"type": "bag", "attributes_list": {}}, {"type": "bottom", "attributes_list": {}}, {"type": "dress", "attributes_list": {}}, {"type": "ethnic_wear", "attributes_list": {}}, {"type": "eyewear", "attributes_list": {}}, {"type": "jewelry", "attributes_list": {}}, {"type": "outerwear", "attributes_list": {}}, {"type": "package", "attributes_list": {}}, {"type": "shoe", "attributes_list": {}}, {"type": "skirt", "attributes_list": {}}, {"type": "top", "attributes_list": {}}, {"type": "watch", "attributes_list": {}}, {"type": "other", "attributes_list": {}}], "im_id": "201710272b0e4197f3b8e7c72ea7b07a7552c4d054062e29.jpg", "reqid": "691101860366505626"}'

        httpretty.register_uri(httpretty.POST, self.discoversearch_entpoint, body=request_callback)

        resp = self.api.discoversearch(im_url="http://www.test.com/test.jpg")
        send_params = self.get_request_params(request_callback.request)

        self.assertEqual(resp['status'], "OK")
        # assert default value
        self.assertEqual(send_params['detection'][0], "all")
        self.assertEqual(send_params['detection_limit'][0], "5")
        self.assertEqual(send_params['result_limit'][0], "10")
        self.assertEqual(send_params['detection_sensitivity'][0], "low")
        self.assertEqual(send_params['im_url'][0], 'http://www.test.com/test.jpg')

    @httpretty.activate
    def test_discoversearch_valid_im_id_with_default_values(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "discoversearch", "error": [], "result_limit": 10, "detection_limit": 5, "page": 1, "objects": [{"type": "top", "attributes": {}, "score": 0.697765052318573, "box": [4, 55, 98, 98], "total": 100, "result": [{"im_name": "KOBO_26a8d231-97ea-477f-816b-f0a9b26935c2", "score": 0.6767474412918091}, {"im_name": "KOBO_6eca8321-f392-43f2-ae7d-6bff567f4218", "score": 0.6764472126960754}, {"im_name": "RAKUTEN-GB_rzcd-46621", "score": 0.6700685620307922}, {"im_name": "KOBO_927ef9af-0f45-4c5e-8dc1-fd01c55ab13f", "score": 0.6667808294296265}, {"im_name": "OVERSTOCK_8343843_11708334", "score": 0.6594167947769165}, {"im_name": "OVERSTOCK_8343843_4359899", "score": 0.6594167947769165}, {"im_name": "KOBO_fad3c7c7-c9da-4063-be25-f9f8c6d9f7ce", "score": 0.6584149599075317}, {"im_name": "KOBO_ea343fd9-0a5a-403a-a2e5-71c7f6ef7fa9", "score": 0.6571913957595825}, {"im_name": "KOBO_5b76493a-63ea-4899-8275-da696b5caa22", "score": 0.6553171873092651}, {"im_name": "KOBO_9e525cd1-5b57-4009-a1df-aafb87766087", "score": 0.6512559056282043}]}], "object_types_list": [{"type": "bag", "attributes_list": {}}, {"type": "bottom", "attributes_list": {}}, {"type": "dress", "attributes_list": {}}, {"type": "ethnic_wear", "attributes_list": {}}, {"type": "eyewear", "attributes_list": {}}, {"type": "jewelry", "attributes_list": {}}, {"type": "outerwear", "attributes_list": {}}, {"type": "package", "attributes_list": {}}, {"type": "shoe", "attributes_list": {}}, {"type": "skirt", "attributes_list": {}}, {"type": "top", "attributes_list": {}}, {"type": "watch", "attributes_list": {}}, {"type": "other", "attributes_list": {}}], "im_id": "201710272b0e4197f3b8e7c72ea7b07a7552c4d054062e29.jpg", "reqid": "691101860366505626"}'

        httpretty.register_uri(httpretty.POST, self.discoversearch_entpoint, body=request_callback)

        resp = self.api.discoversearch(im_id="12345")
        send_params = self.get_request_params(request_callback.request)

        self.assertEqual(resp['status'], "OK")
        # assert default value
        self.assertEqual(send_params['detection'][0], "all")
        self.assertEqual(send_params['detection_limit'][0], "5")
        self.assertEqual(send_params['result_limit'][0], "10")
        self.assertEqual(send_params['detection_sensitivity'][0], "low")
        self.assertEqual(send_params['im_id'][0], '12345')

    @httpretty.activate
    def test_discoversearch_valid_image_with_default_values(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "discoversearch", "error": [], "result_limit": 10, "detection_limit": 5, "page": 1, "objects": [{"type": "top", "attributes": {}, "score": 0.697765052318573, "box": [4, 55, 98, 98], "total": 100, "result": [{"im_name": "KOBO_26a8d231-97ea-477f-816b-f0a9b26935c2", "score": 0.6767474412918091}, {"im_name": "KOBO_6eca8321-f392-43f2-ae7d-6bff567f4218", "score": 0.6764472126960754}, {"im_name": "RAKUTEN-GB_rzcd-46621", "score": 0.6700685620307922}, {"im_name": "KOBO_927ef9af-0f45-4c5e-8dc1-fd01c55ab13f", "score": 0.6667808294296265}, {"im_name": "OVERSTOCK_8343843_11708334", "score": 0.6594167947769165}, {"im_name": "OVERSTOCK_8343843_4359899", "score": 0.6594167947769165}, {"im_name": "KOBO_fad3c7c7-c9da-4063-be25-f9f8c6d9f7ce", "score": 0.6584149599075317}, {"im_name": "KOBO_ea343fd9-0a5a-403a-a2e5-71c7f6ef7fa9", "score": 0.6571913957595825}, {"im_name": "KOBO_5b76493a-63ea-4899-8275-da696b5caa22", "score": 0.6553171873092651}, {"im_name": "KOBO_9e525cd1-5b57-4009-a1df-aafb87766087", "score": 0.6512559056282043}]}], "object_types_list": [{"type": "bag", "attributes_list": {}}, {"type": "bottom", "attributes_list": {}}, {"type": "dress", "attributes_list": {}}, {"type": "ethnic_wear", "attributes_list": {}}, {"type": "eyewear", "attributes_list": {}}, {"type": "jewelry", "attributes_list": {}}, {"type": "outerwear", "attributes_list": {}}, {"type": "package", "attributes_list": {}}, {"type": "shoe", "attributes_list": {}}, {"type": "skirt", "attributes_list": {}}, {"type": "top", "attributes_list": {}}, {"type": "watch", "attributes_list": {}}, {"type": "other", "attributes_list": {}}], "im_id": "201710272b0e4197f3b8e7c72ea7b07a7552c4d054062e29.jpg", "reqid": "691101860366505626"}'

        httpretty.register_uri(httpretty.POST, self.discoversearch_entpoint, body=request_callback)

        resp = self.api.discoversearch(image=self.image_path)
        send_params = self.get_request_params(request_callback.request)

        self.assertTrue(len(send_params) > 1000) # have image content

    @httpretty.activate
    def test_discoversearch_valid_request_with_specified_values(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "discoversearch", "error": [], "result_limit": 10, "detection_limit": 5, "page": 1, "objects": [{"type": "top", "attributes": {}, "score": 0.697765052318573, "box": [4, 55, 98, 98], "total": 100, "result": [{"im_name": "KOBO_26a8d231-97ea-477f-816b-f0a9b26935c2", "score": 0.6767474412918091}, {"im_name": "KOBO_6eca8321-f392-43f2-ae7d-6bff567f4218", "score": 0.6764472126960754}, {"im_name": "RAKUTEN-GB_rzcd-46621", "score": 0.6700685620307922}, {"im_name": "KOBO_927ef9af-0f45-4c5e-8dc1-fd01c55ab13f", "score": 0.6667808294296265}, {"im_name": "OVERSTOCK_8343843_11708334", "score": 0.6594167947769165}, {"im_name": "OVERSTOCK_8343843_4359899", "score": 0.6594167947769165}, {"im_name": "KOBO_fad3c7c7-c9da-4063-be25-f9f8c6d9f7ce", "score": 0.6584149599075317}, {"im_name": "KOBO_ea343fd9-0a5a-403a-a2e5-71c7f6ef7fa9", "score": 0.6571913957595825}, {"im_name": "KOBO_5b76493a-63ea-4899-8275-da696b5caa22", "score": 0.6553171873092651}, {"im_name": "KOBO_9e525cd1-5b57-4009-a1df-aafb87766087", "score": 0.6512559056282043}]}], "object_types_list": [{"type": "bag", "attributes_list": {}}, {"type": "bottom", "attributes_list": {}}, {"type": "dress", "attributes_list": {}}, {"type": "ethnic_wear", "attributes_list": {}}, {"type": "eyewear", "attributes_list": {}}, {"type": "jewelry", "attributes_list": {}}, {"type": "outerwear", "attributes_list": {}}, {"type": "package", "attributes_list": {}}, {"type": "shoe", "attributes_list": {}}, {"type": "skirt", "attributes_list": {}}, {"type": "top", "attributes_list": {}}, {"type": "watch", "attributes_list": {}}, {"type": "other", "attributes_list": {}}], "im_id": "201710272b0e4197f3b8e7c72ea7b07a7552c4d054062e29.jpg", "reqid": "691101860366505626"}'

        httpretty.register_uri(httpretty.POST, self.discoversearch_entpoint, body=request_callback)

        resp = self.api.discoversearch(im_url="http://www.test.com/test.jpg", detection_limit=9, result_limit=8,
                                              detection_sensitivity='high', detection='')
        send_params = self.get_request_params(request_callback.request)

        self.assertEqual(resp['status'], "OK")
        # assert specified value
        self.assertFalse('detection' in send_params)
        self.assertEqual(send_params['detection_limit'][0], "9")
        self.assertEqual(send_params['result_limit'][0], "8")
        self.assertEqual(send_params['detection_sensitivity'][0], "high")

    @httpretty.activate
    def test_discoversearch_valid_request_with_keywords_args(self):
        global active_mock_response

        active_mock_response = 200, '{"status": "OK", "method": "discoversearch", "error": [], "result_limit": 10, "detection_limit": 5, "page": 1, "objects": [{"type": "top", "attributes": {}, "score": 0.697765052318573, "box": [4, 55, 98, 98], "total": 100, "result": [{"im_name": "KOBO_26a8d231-97ea-477f-816b-f0a9b26935c2", "score": 0.6767474412918091}, {"im_name": "KOBO_6eca8321-f392-43f2-ae7d-6bff567f4218", "score": 0.6764472126960754}, {"im_name": "RAKUTEN-GB_rzcd-46621", "score": 0.6700685620307922}, {"im_name": "KOBO_927ef9af-0f45-4c5e-8dc1-fd01c55ab13f", "score": 0.6667808294296265}, {"im_name": "OVERSTOCK_8343843_11708334", "score": 0.6594167947769165}, {"im_name": "OVERSTOCK_8343843_4359899", "score": 0.6594167947769165}, {"im_name": "KOBO_fad3c7c7-c9da-4063-be25-f9f8c6d9f7ce", "score": 0.6584149599075317}, {"im_name": "KOBO_ea343fd9-0a5a-403a-a2e5-71c7f6ef7fa9", "score": 0.6571913957595825}, {"im_name": "KOBO_5b76493a-63ea-4899-8275-da696b5caa22", "score": 0.6553171873092651}, {"im_name": "KOBO_9e525cd1-5b57-4009-a1df-aafb87766087", "score": 0.6512559056282043}]}], "object_types_list": [{"type": "bag", "attributes_list": {}}, {"type": "bottom", "attributes_list": {}}, {"type": "dress", "attributes_list": {}}, {"type": "ethnic_wear", "attributes_list": {}}, {"type": "eyewear", "attributes_list": {}}, {"type": "jewelry", "attributes_list": {}}, {"type": "outerwear", "attributes_list": {}}, {"type": "package", "attributes_list": {}}, {"type": "shoe", "attributes_list": {}}, {"type": "skirt", "attributes_list": {}}, {"type": "top", "attributes_list": {}}, {"type": "watch", "attributes_list": {}}, {"type": "other", "attributes_list": {}}], "im_id": "201710272b0e4197f3b8e7c72ea7b07a7552c4d054062e29.jpg", "reqid": "691101860366505626"}'

        httpretty.register_uri(httpretty.POST, self.discoversearch_entpoint, body=request_callback)

        resp = self.api.discoversearch(im_url="http://www.test.com/test.jpg", detection_limit=9, result_limit=8,
                                              detection_sensitivity='high', detection='', test_kw='test')
        send_params = self.get_request_params(request_callback.request)

        self.assertEqual(resp['status'], "OK")
        # assert specified value
        self.assertFalse('detection' in send_params)
        self.assertEqual(send_params['test_kw'][0], 'test')

if __name__ == '__main__':
    unittest.main()
