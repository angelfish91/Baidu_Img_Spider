#!/usr/bin/evn python2.7
# -*- coding: utf-8 -*-
"""
当前模块仅下载文件

"""
import time
import urlparse

import requests
from contextlib import closing

from config import logger


# 下载文件最大大小 10M
gFileMaxSize = 10*1024*1024
# 设置请求一条URL响应的超时时间
response_timeout = 10
# 下载文件最长时间
download_timeout = 10
# 每次获取文件的每块大小1024字节
get_file_per_block = 1024
# 响应成功的http代号
response_succe_code = 200
# 响应重定向的http代号
response_redirect_code = 300


def __do_download_file(src_url, file_path):
    """
    下载URL对应的文件，仅仅下载URL对应文件功能
    :param src_url: 待下载的URL
    :param file_path: 下载对应的文件路径
    :return:
            result_code: True下载成功，False下载失败
            download_label: 下载状态标签
    """
    result_code = True
    download_label = "download_sucess"

    # 使用GET或OPTIONS时，Requests会自动处理位置重定向。
    with closing(requests.get(src_url, stream=True, timeout=response_timeout)) as response:
        response_code = response.status_code
        # 响应成功，需要下载文件
        if response_code < response_succe_code or response_code > response_redirect_code:
            # 注意 这里是响应失败让上层捕获异常记录日志
            raise Exception("requests get %s url response_code is failue" % src_url)

        content_length = response.headers.get('content-length', "0")
        if content_length.isdigit() and int(content_length) > gFileMaxSize:
            # 日志的存储格式再定，先实现功能框架
            result_code = False
            download_label = "content_length_exceed"
        else:
            downloading_size = 0
            st_time = time.time()
            with open(file_path, 'wb') as wfp:
                for data in response.iter_content(get_file_per_block):
                    if data is None:
                        break

                    ed_time = time.time()
                    if ed_time - st_time > download_timeout:
                        result_code = False
                        download_label = "download_file_timeout"
                        break

                    downloading_size += len(data)
                    if downloading_size > gFileMaxSize:
                        result_code = False
                        download_label = "download_file_large"
                        break

                    wfp.write(data)

    return result_code, download_label


def download_img_file(src_url, file_path):
    """
    外部URL下载文件接口
    :param src_url: URL
    :param file_path: 下载文件存放路径
    :return:
            result_code: True 下载文件成功，下载文件失败
            file_path：对应文件可能存在，可能不存在，result_code为True的时候一定存在
    """

    if src_url is None:
        raise ValueError("download url file url param or url_md5 param is None")

    url_res = urlparse.urlparse(src_url)
    if url_res is None:
        raise ValueError("parse %s url is error, please check this url" % src_url)

    url_scheme = url_res.scheme
    if url_scheme != "http" and url_scheme != "https":
        raise ValueError("only support http or https scheme url:%s" % src_url)

    try:
        result_code, download_label = __do_download_file(src_url, file_path)
    except Exception as e:
        logger.warn("do download %s url file error: %s" % (src_url, str(e)))
        download_label = "request_url_failure"
        result_code = False

    if not result_code:
        logger.warn("do download %s url file error: %s" % (src_url, download_label))
    return result_code
