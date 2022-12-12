# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 13:39
@Auth ： yuming
@File ：main.py
@IDE ：PyCharm
@Motto：A good song never tires of hearing a hundred times, a good book never tires of reading a hundred times
"""
from my_proxy_pool.settings import proxyfetcherSetting, checkSetting

"""采集代理池  
采集线程      存入queue    生产者
检测线程     从queue里 取proxy 测试 代理是否可用  可用的放入redis  消费者 
"""



import asyncio
import re
import threading
from time import sleep

import aiohttp
import requests
import chardet
from aiohttp import ClientConnectorSSLError
from aredis import StrictRedis

from my_proxy_pool.db.redisClient import RedisClient
from queue import Queue
queue=Queue(30)
def main():
    for proxyfetcher in proxyfetcherSetting:
        cls=proxyfetcher.get("cls")
        t=cls(name=proxyfetcher.get("name"),start_url=proxyfetcher.get("start_url"),times=proxyfetcher.get("times",10))
        t.start()

    for check in checkSetting:
        cls=check.get("cls")
        t=cls(hashTableName=check.get("hashTableName"))
        t.start()
        t1 = cls(hashTableName=check.get("hashTableName"))
        t1.start()
        t2 = cls(hashTableName=check.get("hashTableName"))
        t2.start()
        t3 = cls(hashTableName=check.get("hashTableName"))
        t3.start()



if __name__ == "__main__":
    main()