#!/usr/bin/evn python2.7
# -*- coding: utf-8 -*-
import logging
import platform
import re

import signal
import requests
from urlnormalize import UrlNormalize


__limit_time = 60


def time_limit(interval):
    """
    定时器装饰，使用信号量机制进行装饰
    interval:函数结束时间
    alarm信号只在linux环境下有效
    :param interval:
    :return:
    """
    def wraps(func):
        def handler():
            raise RuntimeError('time out while deal func :%s' %(str(func)))

        def deco(*args, **kwargs):
            if platform.system() != 'Windows':
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(interval)
                res = func(*args, **kwargs)
                signal.alarm(0)
            else:
                res = func(*args, **kwargs)
            return res
        return deco
    return wraps


def check_domain(domain):
    """
    检测一个字符串是否是域名
    :param domain: 待检测的字符串
    :return: bool，如果该字符串是域名返回True，否则返回False
    """
    regex_domain = re.compile('(?i)^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
    if regex_domain.match(domain) is None:
        return False
    return True


def check_ip(check_str):
    """
    检测一个字符串是否是IP
    :param check_str: 待检测的字符串
    :return: bool，如果该字符串是IP返回True，否则返回False
    """
    regex_ip = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if regex_ip.match(check_str) is None:
        return False
    return True


def check_url_ml(url):
    """
    检测一个字符串是否是url
    :param url:
    :return: bool，如果该字符串是url返回True，否则返回False
    """
    normalized_url = UrlNormalize(url)
    domain = normalized_url.get_hostname()
    if not check_domain(domain) and not check_ip(domain):
        return False

    url_path = normalized_url.get_path()
    if url_path != '' and url_path.find('/') == -1:
        return False

    return True


@time_limit(__limit_time)
def get_url(url):
    '''
    获取url数据
    :param url:
    :return:
    '''
    if not check_url_ml(url):
        raise ValueError("url is not legal")
    html = ''
    url_code = '404'
    real_url = url
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20131029 Firefox/17.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
    }
    try:
        s = requests.get(url, headers=hdr, timeout=30)
        real_url = s.url
        url_code = s.status_code
        html = s.content
        # 尝试解码，解码失败不做处理
        try:
            html = html.encode('utf-8')
        except:
            pass
    except Exception as e:
        logging.error('%s,%s,some thing is wrong when get url:%s', str(Exception), str(e), url)
    return html, url_code, real_url

