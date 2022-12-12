# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 15:28
@Auth ： yuming
@File ：redisClient.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""

from redis import Redis, BlockingConnectionPool


class RedisClient:
    """

        :param host: host
        :param port: port
        :param password: password
        :param db: db

    """
    def __init__(self,host=None,port=None,db=0,password=None,hashTableName=None):
        self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True, timeout=5,socket_timeout=5,
                    host=host,port=port,db=db))
        self.hashTableName=hashTableName


    def put(self,key,value):
        """

        :param key: hashtable 键 ip:port
        :param value:  hashtable 各属性值
        :return:
        """
        data=self.__conn.hset(self.hashTableName,key,value)
        return data