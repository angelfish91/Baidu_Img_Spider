#!/usr/bin/evn python2.7
# -*- coding: utf-8 -*-
"""
main

"""
import os
from multiprocessing import Process

from config import PAGE_NUM, BASE_IMAGE_PATH, BASE_JSON_PATH
from claw_subpro import img_claw_subpro

def load_task(filepath):
    """
    :param filepath:
    :return:
    """
    search_word_list, label_name_list, label_id_list = list(), list(), list()
    with open(filepath, 'r') as fd:
        data = [_.strip() for _ in fd]
    for line in data:
        a, b, c = line.split(" ")
        search_word_list.append(b)
        label_id_list.append(c)
        label_name_list.append(a)
    return search_word_list, label_name_list, label_id_list


def main(filepath = "label40.txt"):
    """
    :param filepath:
    :return:
    """
    search_word_list, label_name_list, label_id_list = load_task(filepath)

    pool = list()
    for i in range(len(search_word_list)):
        proc = Process(target = img_claw_subpro, args=(search_word_list[i],
                                                       label_id_list[i],
                                                       label_name_list[i],
                                                       os.path.join(BASE_JSON_PATH, label_name_list[i]+".json"),
                                                       os.path.join(BASE_IMAGE_PATH, "spider" + label_name_list[i]),
                                                       PAGE_NUM))
        pool.append(proc)
        proc.start()

    for proc in pool:
        proc.join()


if __name__ == "__main__":
    main()
