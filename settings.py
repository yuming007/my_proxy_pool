# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/12 9:37
@Auth ： yuming
@File ：settings.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""
from my_proxy_pool.fetcher.check import Check
from my_proxy_pool.fetcher.proxyFetcher import ProxyFetcher_66, ProxyFetcher_kuaidaili, ProxyFetcher_yundaili, \
    SampleCheck, ProxyFetcher_fatezero, ProxyFetcher_jiangxianli, ProxyFetcher_89

proxyfetcherSetting=[
    {"cls":ProxyFetcher_66,"name":"66代理","start_url":"http://www.66ip.cn","times":999},
    {"cls":ProxyFetcher_kuaidaili,"name":"快代理","start_url":"https://www.kuaidaili.com/free/inha/","times":999},
    {"cls":ProxyFetcher_yundaili,"name":"云代理","start_url":"http://www.ip3366.net/free/","times":999},
    {"cls":ProxyFetcher_fatezero,"name":"fatezero","start_url":"http://proxylist.fatezero.org/proxy.list"},
    {"cls":ProxyFetcher_jiangxianli,"name":"jiangxianli","start_url":"https://ip.jiangxianli.com/blog.html?page=1"},
    {"cls":ProxyFetcher_89,"name":"89代理","start_url":"https://www.89ip.cn/","times":999},
]



checkSetting=[
    {"cls":SampleCheck,"hashTableName":"my_porxy_pool"}
]