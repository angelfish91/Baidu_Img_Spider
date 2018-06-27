#!/usr/bin/evn python2.7
# -*- coding: utf-8 -*-
"""
config

"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

MULTIPROCESS_NUM = 2
PAGE_NUM = 200
IMG_FMT = ['jpg']
BASE_IMAGE_PATH = "./"
BASE_JSON_PATH = "./json"
