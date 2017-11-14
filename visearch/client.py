import os
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from PIL import Image
from requests.auth import HTTPBasicAuth
from six.moves.urllib.parse import quote
from .bind import bind_method, build_parameters, build_path
from .bind import ViSearchClientError


class ViSearchAPI(object):
    def __init__(self, access_key, secret_key, host="http://visearch.visenze.com/"):
        # self.host = "http://visearch.visenze.com/"
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key
        self.auth_info = HTTPBasicAuth(self.access_key, self.secret_key)

    def insert(self, images, **kwargs):
        if type(images).__name__ != 'list':
            images = [images, ]

        path = 'insert'
        required_fields = ['im_name', 'im_url']
        method = 'POST'
        raw_parameters = {
            'images': images,
        }
        data = build_parameters(path, raw_parameters, required_fields)
        data.update(kwargs)
        resp = bind_method(self, path, method, data=data)
        return resp

    def update(self, images, **kwargs):
        if type(images).__name__ != 'list':
            images = [images, ]

        path = 'insert'
        required_fields = ['im_name']
        method = 'POST'
        raw_parameters = {
            'images': images,
        }
        data = build_parameters(path, raw_parameters, required_fields)
        data.update(kwargs)
        resp = bind_method(self, path, method, data=data)
        return resp

    def remove(self, image_names, **kwargs):
        if type(image_names).__name__ != 'list':
            image_names = [image_names, ]
        path = 'remove'
        method = 'POST'
        data = build_parameters(path, image_names)
        data.update(kwargs)
        resp = bind_method(self, path, method, data=data)
        return resp

    def insert_status(self, trans_id, error_page=None, error_limit=None):
        path = 'insert/status/{trans_id}'
        path_parameters = {
            'trans_id': str(trans_id)
        }
        if error_page:
            path_parameters['error_page'] = error_page
        if error_limit:
            path_parameters['error_limit'] = error_limit
        path = build_path(path, path_parameters)
        resp = bind_method(self, path, 'GET')
        return resp

    def _search(self, path, parameters, **kwargs):
        parameters = build_parameters(path, parameters, **kwargs)
        resp = bind_method(self, path, 'GET', parameters)
        return resp

    def search(self, im_name, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0, get_all_fl=False, **kwargs):
        parameters = {
            'im_name': im_name,
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min,
            'get_all_fl': get_all_fl
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})

        path = 'search'
        return self._search(path, parameters, **kwargs)

    def recommendation(self, im_name, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0, get_all_fl=False, **kwargs):
        parameters = {
            'im_name': im_name,
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min,
            'get_all_fl': get_all_fl
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})

        path = 'recommendation'
        parameters = build_parameters(path, parameters, **kwargs)
        resp = bind_method(self, path, 'GET', parameters)
        return resp

    def colorsearch(self, color, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0, get_all_fl=False, **kwargs):
        # _rgbstr = re.compile(r'^(?:[0-9a-fA-F]{3}){1,2}$')
        if color.startswith('#'):
            color = color[1:]
        # if not bool(_rgbstr.match(color)):
        #     raise ViSearchClientError("the color {} is not in 6 character hex format".format(color))
        parameters = {
            'color': color,
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min,
            'get_all_fl': get_all_fl
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})

        path = 'colorsearch'
        return self._search(path, parameters, **kwargs)

    def _read_image(self, image_path, resize_settings, validation_func=None):
        image = Image.open(image_path)

        if resize_settings:
            if resize_settings == 'STANDARD':
                dimensions, quality = (512, 512), 75
            elif resize_settings == 'HIGH':
                dimensions, quality = (1024, 1024), 75
            else:
                resize_type_name = type(resize_settings).__name__
                if (resize_type_name == 'list' or resize_type_name == 'tuple') and len(resize_settings) == 3:
                    dimensions, quality = (resize_settings[0], resize_settings[1]), resize_settings[2]
                else:
                    raise ViSearchClientError("invalid resize settings: {0}".format(resize_settings))

            image = image.resize(dimensions, Image.ANTIALIAS)

            output = StringIO()
            image.save(output, 'JPEG', quality=quality)
            contents = output.getvalue()
            size = len(contents)
            output.close()
            fp = (image_path, contents)
            files = {'image': fp}
        else:
            filename = os.path.basename(image_path)
            files = {'image': (filename, open(image_path, 'rb'), 'application/octet-stream')}
            size = os.path.getsize(image_path)

        width, height = image.size
        if validation_func:
            validation_func(width, height, size)

        image.close()

        return files

    def uploadsearch(self, image_path=None, image_url=None, box=None, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0, resize=None, get_all_fl=False, **kwargs):
        parameters = {
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min,
            'get_all_fl': get_all_fl
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})
        if box:
            if (type(box).__name__ == 'list' or type(box).__name__ == 'tuple') and len(box) == 4:
                parameters.update({'box': ','.join(map(str, box))})
            else:
                raise ViSearchClientError("invalid box: {0}".format(box))

        path = 'uploadsearch'

        if not (image_path or image_url):
            raise ViSearchClientError("either provide image_path or image_url")
        elif image_url:
            parameters.update({'im_url': quote(image_url)})
            return self._search(path, parameters, **kwargs)
        else:
            if resize:
                files = self._read_image(image_path, resize)
            else:
                filename = os.path.basename(image_path)
                files = {'image': (filename, open(image_path, 'rb'), 'application/octet-stream')}
            parameters = build_parameters(path, parameters, **kwargs)
            return bind_method(self, path, 'POST', parameters, files=files)

    def discoversearch(self, im_url=None, image=None, im_id=None, detection="all",
                       detection_limit=5, detection_sensitivity="low", result_limit=10, box=None, **kwargs):
        parameters = {
            "detection_limit": detection_limit,
            "detection_sensitivity": detection_sensitivity,
            "result_limit": result_limit,
            "detection": detection
        }
        path = 'discoversearch'
        files = None

        if box:
            if (type(box).__name__ == 'list' or type(box).__name__ == 'tuple') and len(box) == 4:
                parameters.update({'box': ','.join(map(str, box))})
            else:
                raise ViSearchClientError("invalid box: {0}".format(box))

        if not (im_url or image or im_id):
            raise ViSearchClientError("at least one of `im_url`, `image` or `im_id` must exists")
        elif im_url:
            parameters['im_url'] = im_url
        elif image:
            def validation(width, height, size):
                # if width < 100 or height < 100:
                #     raise ViSearchClientError("width and height of the image must be larger than 100px")

                if size > 10 * pow(2, 20): # larger than 10MB
                    raise ViSearchClientError("file size should not larger than 10MB")

            files = self._read_image(image, None, validation_func=validation)
        else:
            parameters['im_id'] = im_id

        parameters.update(kwargs)
        return bind_method(self, path, 'POST', data=parameters, files=files)