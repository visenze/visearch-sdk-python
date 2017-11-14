import requests
import re
from six.moves.urllib.parse import quote
from . import __version__


re_path_template = re.compile('{\w+}')


class ViSearchClientError(Exception):
    def __init__(self, error_message, status_code=None):
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        if self.status_code:
            return "(%s) %s" % (self.status_code, self.error_message)
        else:
            return self.error_message


class ViSearchAPIError(Exception):

    def __init__(self, status_code, error_type, error_message, *args, **kwargs):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return "(%s) %s-%s" % (self.status_code, self.error_type, self.error_message)


def build_path(path, parameters):
    for variable in re_path_template.findall(path):
        name = variable.strip('{}')

        try:
            value = quote(parameters[name])
        except KeyError:
            raise Exception('No parameter value found for path variable: %s' % name)
        del parameters[name]

        path = path.replace(variable, value)

    return path


def build_parameters(path, raw_parameters, required_fields=None, **kwargs):
    if path == 'insert':
        images = raw_parameters['images']

        for ind, image in enumerate(images):
            is_required_fields_provided = all(attr_name in image.keys() for attr_name in required_fields)
            if not is_required_fields_provided:
                error_message = "insert api: the {0}'s image doesn't provide the required fields".format(ind)
                raise ViSearchClientError(error_message)

        param = {}
        for ind, image in enumerate(images):
            for attr_name, attr_value in image.items():
                param['%s[%d]' % (attr_name, ind)] = attr_value

    elif path == 'remove':
        param = dict([('im_name[{}]'.format(ind), image_name) for ind, image_name in enumerate(raw_parameters)])

    elif path in ['search', 'colorsearch', 'uploadsearch', 'recommendation', 'discoversearch']:
        parameter_list = []
        for attr_name, attr_value in raw_parameters.items():
            parameter_item = '{0}={1}'.format(attr_name, attr_value)
            if attr_name == 'fl':
                if type(attr_value) == list or type(attr_value) == tuple:
                    parameter_item = '&'.join(['fl={0}'.format(fl_val) for fl_val in attr_value])
            elif attr_name == 'fq':
                if type(attr_value) == dict:
                    parameter_item = '&'.join(['fq={0}:{1}'.format(fq_attr, fq_val) for fq_attr, fq_val in attr_value.items()])
            parameter_list.append(parameter_item)

        parameter_list += ['{}={}'.format(key, value) for key, value in kwargs.items()]
        param = '&'.join(parameter_list)

    return param


def bind_method(api, path, method, parameters=None, data=None, files=None):
    headers = {'X-Requested-With': 'ViSenze-Python-SDK/{}'.format(__version__)}

    if method.upper() == 'POST':
        resp = requests.post(
            api.host + path,
            params=parameters,
            data=data,
            files=files,
            auth=api.auth_info,
            timeout=10 * 60,
            headers=headers)
    elif method.upper() == 'GET':
        resp = requests.get(
            api.host + path,
            params=parameters,
            files=files,
            auth=api.auth_info,
            timeout=10 * 60,
            headers=headers)
    else:
        raise ViSearchClientError('unsupported http method')

    if resp.status_code != 200:
        raise ViSearchAPIError(resp.status_code, "{0} error".format(path), "{0} error".format(path))

    resp_data = resp.json()

    return resp_data
