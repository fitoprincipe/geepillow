# coding=utf-8
import ee
import os
import requests
from typing import Union
from pathlib import Path


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


def download_file(url: str, path: Union[str, Path]):
    """ Download a file from a given url

    Args:
        url: full url
        path: path to save the downloaded file
    """
    response = requests.get(url, stream=True)
    code = response.status_code

    while code != 200:
        if code == 400:
            return None
        response = requests.get(url, stream=True)
        code = response.status_code
        size = response.headers.get('content-length', 0)
        if size: print('size:', size)

    with open(path, "wb") as handle:
        for data in response.iter_content():
            handle.write(data)

    return handle

def array_from_list(alist: list, n_columns: int) -> list:
    """Create a 2D list (array) from a list"""
    n_rows = len(alist) // n_columns
    if len(alist) % n_columns > 0:
        n_rows += 1

    final = []
    # Create the 2D array
    array = [[None] * n_columns for _ in range(n_rows)]
    return array
