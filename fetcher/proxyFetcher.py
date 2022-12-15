# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 13:55
@Auth ： yuming
@File ：proxyFetcher.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""
import asyncio
import json
import re
import threading
from time import sleep

import aiohttp
import requests
import chardet
from aiohttp import ClientConnectorSSLError
from aredis import StrictRedis

from my_proxy_pool.db.redisClient import RedisClient


from my_proxy_pool.fetcher.proxy import Proxy
from my_proxy_pool.mq.stream import myRedisMq
from my_proxy_pool.parser.parse import XmlParser
from queue import Queue
queue=Queue(30)

class ProxyFetcher(threading.Thread):
    """
            代理获取类
    """
    def __init__(self,name=None,start_url=None,sleep=20,
                 starttime=0,times=10,domainName=None,
                 next_lunci_sleep=60*60*6,mq=None):
        super().__init__()
        self.name=name
        self.url=start_url
        self.HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                  'Accept': '*/*',
                  'Connection': 'keep-alive',
                  'Accept-Language': 'zh-CN,zh;q=0.8'}
        self.the_url=""
        self.sleep=sleep
        self.times=times
        self.nowtime=starttime
        self.domainName=domainName
        self.next_lunci_sleep=next_lunci_sleep
        self.mq=mq

    def run(self):
        self.the_url = self.url
        while True:
            while self.nowtime<=self.times:
                try:
                    resp = requests.get(self.the_url, headers=self.HEADER)
                    self.respText = self.getText(resp)
                    self.xmlParse = XmlParser(self.respText).get_parse()
                    self.parse()
                    self.next()
                except Exception as e:
                    print(e)
                    continue
                sleep(self.sleep)
                self.nowtime+=1
            print(f"{self.name}当前轮次已结束")
            sleep(self.next_lunci_sleep)
            self.the_url = self.url
            self.nowtime = 0
    def parse(self):
        pass
    def next(self):
        """
        下一页
        :return:  下一页的url
        """
        pass
    def getText(self,resp):
        """
           获取报文   文本信息
        :param resp:
        :return:
        """

        encoding_type=chardet.detect(resp.content)
        _type = encoding_type.get("encoding")
        if _type == "Windows-1254":
            _type = "utf-8"

        return resp.content.decode(_type)



class ProxyFetcher_66(ProxyFetcher):
    def parse(self):
        trs = self.xmlParse.xpath("//div[@class='layui-row layui-col-space15']//table/tr")
        for item in trs[1:]:
            ip = item.xpath("./td[1]/text()")[0].strip()
            port = item.xpath("./td[2]/text()")[0].strip()
            loation = item.xpath("./td[3]/text()")[0].strip()
            porxy = Proxy(ip=ip, port=port, loation=loation,name=self.name)
            data = {"ip": ip, "port": port, "loation": loation, "name": self.name}
            self.mq.add_msg(data=data)
    def next(self):
        next_url = self.xmlParse.xpath('//div[@id="PageList"]//a[last()]/@href')[0]
        self.the_url = self.url + next_url


class ProxyFetcher_kuaidaili(ProxyFetcher):
    """
       快代理   https://www.kuaidaili.com/free/inha/
    """
    def parse(self):
        trs = self.xmlParse.xpath("//div[@id='list']//table/tbody/tr")
        for item in trs[1:]:
            ip = item.xpath("./td[1]/text()")[0].strip()
            port = item.xpath("./td[2]/text()")[0].strip()
            loation = item.xpath("./td[5]/text()")[0].strip()
            porxy = Proxy(ip=ip, port=port, loation=loation,name=self.name)
            data = {"ip": ip, "port": port, "loation": loation, "name": self.name}
            self.mq.add_msg(data)

    def next(self):
        self.the_url = self.url+str(self.nowtime)



class ProxyFetcher_yundaili(ProxyFetcher):
    """云代理        http://www.ip3366.net/free/"""

    def parse(self):
        trs = self.xmlParse.xpath("//div[@id='list']//table/tbody/tr")
        for item in trs[1:]:
            ip = item.xpath("./td[1]/text()")[0].strip()
            port = item.xpath("./td[2]/text()")[0].strip()
            loation = item.xpath("./td[5]/text()")[0].strip()
            porxy = Proxy(ip=ip, port=port, loation=loation,name=self.name)
            data = {"ip": ip, "port": port, "loation": loation, "name": self.name}
            self.mq.add_msg(data)
    def next(self):
        next_url = self.xmlParse.xpath('//div[@id="listnav"]//a[last()-1]/@href')[0]
        self.the_url = self.url + next_url



class ProxyFetcher_fatezero(ProxyFetcher):
    def run(self):
        while True:
            self.the_url = self.url
            try:
                resp = requests.get(self.the_url, headers=self.HEADER)
                respText = resp.text
            except:
                pass
            else:
                for i in respText.split("\n"):
                    d=json.loads(i)
                    ip=d.get("host")
                    port=d.get("port")
                    porxy = Proxy(ip=ip, port=port,name=self.name)
                    data = {"ip": ip, "port": port, "loation": "", "name": self.name}
                    self.mq.add_msg(data)
            sleep(60*60*6)



class ProxyFetcher_jiangxianli(ProxyFetcher):
    def parse(self):
        ps=self.xmlParse.xpath("//div[@class='contar-wrap']//div[@class='item']//p/text()")
        for text in ps:
            compile=re.compile(r"(?P<ip>(?:1\d{2}|2[0-3]\d|[1-9]\d|[1-9])\.(?:(?:1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.){2}(?:1\d{2}|2[0-4]\d|25[0-4]|[1-9]\d|[1-9]))\:(?P<port>\d{1,5})")
            result=compile.findall(text)
            for item in result:
                ip = item[0]
                port = item[1]
                porxy = Proxy(ip=ip, port=port,name=self.name)
                data = {"ip": ip, "port": port, "loation": "", "name": self.name}
                self.mq.add_msg(data)

    def next(self):
        next_url = self.xmlParse.xpath('//a[@class="layui-btn layui-btn-normal"]/@href')[0]
        self.the_url = self.url + next_url


class ProxyFetcher_89(ProxyFetcher):
    def parse(self):
        trs = self.xmlParse.xpath("//table[@class='layui-table']/tbody/tr")
        for item in trs:
            ip = item.xpath("./td[1]/text()")[0].strip()
            port = item.xpath("./td[2]/text()")[0].strip()
            loation = item.xpath("./td[3]/text()")[0].strip()
            porxy = Proxy(ip=ip, port=port, loation=loation, name=self.name)
            data={"ip":ip,"port":port,"loation":loation,"name":self.name}
            self.mq.add_msg(data)
    def next(self):
        next_url = self.xmlParse.xpath('//a[@class="layui-laypage-next"]/@href')[0]
        self.the_url = self.url + next_url





class SampleCheck(threading.Thread):
    def __init__(self,hashTableName=None,mq=None,streamName="mystream5",groupName="group1",consumerName="consumer1"):
        super().__init__()
        self.HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                       'Accept': '*/*',
                       'Connection': 'keep-alive',
                       'Accept-Language': 'zh-CN,zh;q=0.8'}
        self.hashTableName=hashTableName
        self.mq=mq
        self.groupName=groupName
        self.consumerName=consumerName
        self.streamName=streamName
    """检测代理是否可用"""
    def run(self):
        redisCilent = RedisClient(host="127.0.0.1", port=6379, db=0, hashTableName=self.hashTableName)
        self.mq.group_if_exist(self.groupName)
        while True:
            id, result = self.mq.read_msg(groupName=self.groupName,consumerName=self.consumerName)
            print(f"消费者{self.groupName}-{self.consumerName}消费一条数据,id:{id},数据:{result}")
            ip=result.get("ip")
            port=result.get("port")
            name=result.get("name")
            loation=result.get("loation")

            proxy=f"{ip}:{port}"
            proxies = {"https": "https://{proxy}".format(proxy=proxy)}
            try:
                resp=requests.get(url="http://www.baidu.com",headers=self.HEADER,proxies=proxies,timeout=4)
                flag=True if resp.status_code==200 else False
            except Exception as e:
                flag=False
            if flag:
                print("success:",ip+port+loation+name)
                data=redisCilent.put(proxy,loation+name)
                print(data)
            self.mq.xack(self.groupName, id)
            sleep(1)
            #queue.task_done()

class Check_Aysncio(threading.Thread):
    def __init__(self):
        super().__init__()
        self.HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                       'Accept': '*/*',
                       'Connection': 'keep-alive',
                       'Accept-Language': 'zh-CN,zh;q=0.8'}
        self.client = StrictRedis(host='127.0.0.1', port=6379, db=0)
    """检测代理是否可用"""
    async def check(self):
        global queue
        while True:
            async with aiohttp.ClientSession() as session:
                try:
                    the_proxy = queue.get()
                    ip = the_proxy.ip
                    port = the_proxy.port
                    name = the_proxy.name
                    proxy = f"{ip}:{port}"
                    proxy=f"https://{proxy}"
                    async with session.head(url="https://www.baidu.com", proxy=proxy, timeout=5) as resp:
                        state_code = resp.status
                        if state_code == 200:
                            print("success:",the_proxy)
                            await self.client.hset("my_porxy_pool", proxy,the_proxy.loation+name)
                except asyncio.TimeoutError as e:
                    print("error", the_proxy)
                except ClientConnectorSSLError as e:
                    pass
                except Exception:
                    continue
                finally:
                    await asyncio.sleep(3)
    async def main(self):
        #await self.client.flushdb()
        tasks=[asyncio.create_task(self.check()) for _ in range(5)]
        result=await asyncio.gather(*tasks)
    def run(self):
        asyncio.run(self.main())


if __name__ == "__main__":
    mq=myRedisMq("mystream5")
    the_fetcher=ProxyFetcher_89(name="89代理",start_url="https://www.89ip.cn/",mq=mq)
    the_fetcher.start()

    the_Check=SampleCheck(hashTableName="my_porxy_pool",
                          mq=mq,groupName="group1",
                          consumerName="consumer1")
    the_Check.start()
