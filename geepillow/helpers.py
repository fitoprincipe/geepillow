# coding=utf-8
import ee
import os


def split(alist, split):
    """ split a list into 'split' items """
    newlist = []
    accum = []
    for i, element in enumerate(alist):
        accum.append(element)
        if (len(accum) == split) or (i == len(alist)-1):
            newlist.append(accum)
            accum = []

    return newlist


def listEE2list(listEE, type='Image'):
    relation = {'Image': ee.Image,
                'Number': ee.Number,
                'String': ee.String,
                'Feature': ee.Feature}
    size = listEE.size().getInfo()
    newlist = []
    for el in range(size):
        newlist.append(relation[type](listEE.get(el)))

    return newlist


def downloadFile(url, name, extension, path=None):
    """ Download a file from a given url

    :param url: full url
    :type url: str
    :param name: name for the file (can contain a path)
    :type name: str
    :param extension: extension for the file
    :type extension: str
    :return: the created file (closed)
    :rtype: file
    """
    import requests
    response = requests.get(url, stream=True)
    code = response.status_code

    if path is None:
        path = os.getcwd()

    pathname = os.path.join(path, name)

    while code != 200:
        if code == 400:
            return None
        response = requests.get(url, stream=True)
        code = response.status_code
        size = response.headers.get('content-length',0)
        if size: print('size:', size)

    with open('{}.{}'.format(pathname, extension), "wb") as handle:
        for data in response.iter_content():
            handle.write(data)

    return handle