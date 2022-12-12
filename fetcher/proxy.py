# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 15:04
@Auth ： yuming
@File ：proxy.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""


class Proxy:
    def __init__(self,ip=None,port=None,loation="None",name=None):
        self.ip=ip
        self.port=port
        self.loation=loation
        self.name=name

    def __str__(self):
        return f"{self.ip}:{self.port}地点：{self.loation}来源：{self.name}"

p=Proxy(ip="sd")
print(p)

