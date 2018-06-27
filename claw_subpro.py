#!/usr/bin/evn python2.7
# -*- coding: utf-8 -*-
"""
爬虫主进程

"""
import os
import re
import json
import urllib
from threading import Thread

from lib.utils import get_url
from lib.dowload_file import download_img_file
from config import logger, IMG_FMT

BASE_URL = "http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq\
=1526302480089_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&ctd=1526302480090%5E00_13\
49X637&word="


class BaiduImageClawer(object):
    """
    baidu clawer class

    """
    def __init__(self, search_word, label_id, label_name, json_file, output_path, page_num):
        """
        爬虫初始化

        :param search_word:
        :param label_id:
        :param label_name:
        :param json_file:
        :param output_path:
        :param page_num:
        """
        self.search_word = search_word
        self.label_id = label_id
        self.label_name = label_name
        self.page_num = page_num
        self.dowload_img_url_set = set()
        self.url_todo = list()
        self.url_done = list()
        self.img_urls = list()

        # 初始化url_todo
        self.url_todo.append(BASE_URL + urllib.quote_plus(self.search_word))

        # img 路径检查
        self.output_path = os.path.abspath(output_path)
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)
            logger.info("make dirs %s" % self.output_path)

        # json 路径检查
        if os.path.isfile(json_file):
            os.remove(json_file)
        self.json_filepath, self.json_filename = os.path.split(json_file)
        self.json_filepath = os.path.abspath(self.json_filepath)
        if not os.path.isdir(self.json_filepath):
            os.makedirs(self.json_filepath)
            logger.info("make dirs %s" % self.json_filepath)
        self.json_filepath = os.path.join(self.json_filepath, self.json_filename)

    def get_img_urls(self, html):
        """
        获取图片链接
        :param html:
        :return:
        """
        assert len(IMG_FMT) > 0
        pattern = r'('
        for fmt in IMG_FMT:
            pattern += 'http:\/\/[^\s,"]*\.%s|https:\/\/[^\s,"]*\.%s|' % (fmt, fmt)
        pattern = pattern[:-1] + r')'
        pattern = re.compile(pattern)
        self.img_urls = re.findall(pattern, html)

    def update_task_list(self, src_url):
        """
        跟新待爬取与已爬取列表
        :param src_url:
        :return:
        """
        self.url_done.append(src_url)
        html, url_code, real_url = get_url(src_url)
        if url_code != 200:
            logger.error("get url error，url code %s, url %s" % (url_code, src_url))
            return
        # 若请求成功,首先跟新img url列表
        self.get_img_urls(html)
        # 若请求成功，跟新待爬取URL列表
        pattern = re.compile(r'(\/search\/flip[^\s,"]*height=0)')
        re_res = re.findall(pattern, html)
        for res in re_res:
            url_todo_tmp = 'http://image.baidu.com' + res
            if url_todo_tmp not in self.url_done:
                self.url_todo.append(url_todo_tmp)
        logger.info("url_todo:%d\turl_done%d" % (len(self.url_todo), len(self.url_done)))

    def img_urls_claw(self):
        """
        单页面爬取图片
        :return:
        """
        json_str, img_url_do, file_path_do = list(), list(), list()
        for index, img_url in enumerate(self.img_urls):
            if img_url in self.dowload_img_url_set:
                continue
            file_name = "".join([self.label_name, "_", str(len(self.dowload_img_url_set)), ".jpg"])
            file_path = os.path.join(self.output_path, file_name)
            img_url_do.append(img_url)
            file_path_do.append(file_path)
            self.dowload_img_url_set.add(img_url)

            json_str.append(json.dumps(
                {"image_url": img_url,
                 "label_id": self.label_id,
                 "image_id": file_path}))

        with open(self.json_filepath, 'a+') as fd:
            for i in json_str:
                fd.write(i+'\n')

        thread_list = []
        for img_url, file_path in zip(img_url_do, file_path_do):
            logger.info("[Downding] %s" % img_url)
            td = Thread(target=download_img_file, args=(img_url, file_path))
            td.start()
            thread_list.append(td)

        for td in thread_list:
            td.join()

    def do_claw(self):
        """
        爬虫主函数

        :return:
        """
        for page_index in range(self.page_num):
            url_exe = ""
            logger.info('-' * 50 + 'page:%d' % page_index + '-' * 50)
            try:
                url_exe = self.url_todo.pop(0)
            except IndexError as err:
                logger.warning("Page:%d  approach to page index limit! %s" % (page_index, err))
            self.update_task_list(url_exe)
            self.img_urls_claw()


def img_claw_subpro((search_word, label_id, label_name, json_file, output_path, page_num)):
    claw_obj = BaiduImageClawer(search_word, label_id, label_name, json_file, output_path, page_num)
    claw_obj.do_claw()


if __name__ == "__main__":
    search_word = "宇宙"
    label_id = 10
    label_name = "space"
    json_file = "./test.json"
    output_path = "./test"
    page_num = 10

    claw_obj = BaiduImageClawer((search_word, label_id, label_name, json_file, output_path, page_num))
    claw_obj.do_claw()
