# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/14 14:59
@Auth ： yuming
@File ：stream.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""
#消息队列表
#Redis Stream 有一个消息链表，将所有加入的消息都串起来，
# 每个消息都有一个唯一的 ID 和对应的内容。每个 Stream 都有唯一的名称，
# 它就是 Redis 的 key，在我们首次使用 xadd 指令追加消息时自动创建。
#优点：持久化存储   主从复制功能


#组成：消息本身   生产者  消费者  消费者组

#一个 Stream 队列可以拥有多个消费组，
# 每个消费组中又包含了多个消费者，组内消费者之间存在竞争关系。
# 当某个消费者消费了一条消息时，同组消费者，都不会再次消费这条消息

#消息列表名称:mystream
#组名称：group1
#消费者名称：consumer1

#todo:创建一个stream并加入消息   xadd mystream * name jack age 12
#*:使用时间戳来创建id

#todo:查看消息列表  xrange mystream - +

#todo: 读取指定消息列表指定id   xread count 2 streams mystream id

#todo:创建消费组 xgroup create mystream group1 $
#$ 从尾部开始消费

#todo:消费组中消费者读取消息
# xreadgroup group group1 consumer1 count 1 block 1000 streams mystream >
#每当消费一个信息 消费组游标就前移一位
#如果不设置则一直等待
#block 1000 等待1000毫秒   如果没有消息来则返回nil


#todo:响应消息  XACK mystream mygroup id
# XPENDING  待处理的消息


#todo:xpending mystream5 group1
#拿出  消费者组从队列里拿出消息 但是没有ack


#todo:xtrim mystrem maxlen=100
#控制队列的最大长度
#如果超过最大长度则会删除旧的



import threading
from time import sleep

import redis



class myRedisMq:
    def __init__(self,streamName):
        self.client=redis.Redis()
        self.streamName=streamName

    def add_msg(self,data={}):
        id = (self.client.xadd(name=self.streamName, id="*", maxlen=6000,fields=data)).decode("utf-8")
        self.client.xlen(self.streamName)
        sleep(1)
        return id
    def xrange_strem(self,start_id=None,end_id=None):
        if not start_id and not end_id:
            start_id ="-"
            end_id="+"
        result=self.client.xrange(name=self.streamName,min=start_id,max=end_id)
    def group_if_exist(self,groupName):
        result = self.client.xinfo_groups(self.streamName)
        flag = False
        for item in result:
            if item['name'].decode("utf-8") == groupName:
                flag = True
        if not flag:
            self.createGroup(groupName)
    def createGroup(self,groupName):
        return self.client.xgroup_create(name=self.streamName,groupname=groupName)
    def createConsumer(self,groupName,consumerName):
        return self.client.xgroup_createconsumer(name=self.streamName,groupname=groupName,consumername=consumerName)
    def read_msg(self,groupName="",consumerName="",count=1,id=">",block=0):
        #xreadgroup group group1 consumer1 count 1 block 1000 streams mystream >
        d={self.streamName:id}
        result=(self.client.xreadgroup(streams=d,groupname=groupName,consumername=consumerName,count=count,block=block))
        d = result[0][1][0][1]
        new = {}
        for key, value in d.items():
            new[key.decode("utf-8")] = value.decode("utf-8")
        return result[0][1][0][0].decode("utf-8"),new
        #createConsumer("mystream2","group1","consumer1")
        #read_msg("mystream2","group1","consumer1")
    def xack(self,groupName,id):
        return self.client.xack(self.streamName,groupName,id)

    # 获取被耽误的消息
    def get_pending_info(self,groupName):
        pending_info = self.client.xpending(self.streamName, groupName)
        min = pending_info["min"].decode("utf-8")
        max = pending_info["max"].decode("utf-8")
        self.xrange_strem(self.streamName, min, max)
        return pending_info





class producer(threading.Thread):
    def __init__(self,streamName,groupName,myRedisMq):
        super().__init__()
        self.myRedisMq=myRedisMq
        self.streamName=streamName
        self.groupName=groupName
        self.myRedisMq.group_if_exist(self.streamName,self.groupName)
        #self.myRedisMq.client.xtrim(name=streamName, maxlen=3)



    def run(self):
        while True:
            d={"name":"testname","age":"123"}
            id=self.myRedisMq.add_msg(d)
            print(f"生产者发送数据至{self.streamName}，id:{id},数据:{d}")
            sleep(0.1)


class Consumer(threading.Thread):
    def __init__(self, streamName, groupName,myRedisMq,consumerName):
        super().__init__()
        self.myRedisMq = myRedisMq
        self.streamName = streamName
        self.groupName = groupName
        self.consumerName = consumerName
        self.myRedisMq.group_if_exist(self.streamName, self.groupName)



    def run(self):
        while True:
            id,result=self.myRedisMq.read_msg(self.groupName,"consumer2")
            print(f"消费者{self.consumerName}消费一条数据,id:{id},数据:{result}")
            self.myRedisMq.xack(self.streamName,self.groupName,id)
            sleep(0.5)


if __name__ == "__main__":
    #myRedisMq=myRedisMq("mystream5")
    #myRedisMq.group_if_exist("mystream5","group7")
    p=producer("mystream5","group1",myRedisMq)
    sleep(1)
    c2=Consumer("mystream5","group1",myRedisMq,consumerName="consumer2")
    c3=Consumer("mystream5","group1",myRedisMq,consumerName="consumer3")
    c4=Consumer("mystream5","group1",myRedisMq,consumerName="consumer4")
    c5=Consumer("mystream5","group1",myRedisMq,consumerName="consumer5")
    p.start()
    sleep(1)
    # c2.start()
    # c3.start()
    # c4.start()
    # c5.start()