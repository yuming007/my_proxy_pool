# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 17:51
@Auth ： yuming
@File ：check_in_redis.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""
import random

from aiohttp import ClientConnectorSSLError

"""再次  检查redis里的代理是否可用"""

import asyncio
from aredis import StrictRedis
import threading
import aiohttp
import ssl
import certifi

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


class testUseful(threading.Thread):

    def __init__(self):
        super().__init__()
        self.client = StrictRedis(host='127.0.0.1', port=6379, db=0)


    async def get_and_test(self):
        while True:
            all=await self.client.hkeys('my_porxy_pool')
            if not all:
                break
            one=random.choice(all).decode("utf-8")
            proxy=f"https://{one}"

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.head(url="http://www.baidu.com",proxy=proxy,timeout=4,ssl=ssl_context) as resp:
                        state_code=resp.status
                        if state_code==200:
                            print("success again:",one)
                except asyncio.TimeoutError as e:
                    print("error again:",one)
                    await self.client.hdel("my_porxy_pool",one)
                except ClientConnectorSSLError as e:
                    pass
                except Exception:
                    continue
                finally:
                    await asyncio.sleep(1)
        return None


    async def main(self):
        #await self.client.flushdb()
        tasks=[asyncio.create_task(self.get_and_test()) for _ in range(2)]
        result=await asyncio.gather(*tasks)


    def run(self):
        asyncio.run(self.main())



t=testUseful()
t.start()





