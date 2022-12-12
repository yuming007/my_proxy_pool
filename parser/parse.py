# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 14:29
@Auth ： yuming
@File ：parse.py
@IDE ：PyCharm
@Motto：Proud, eager, happy and ambitious
"""

from lxml import etree
class Parser:
    """
    网页解析类
    """
    def __init__(self,html=None):
        self.html=html
        self.tree = etree.HTML(html)

    def get_parse(self):
        pass

class XmlParser(Parser):
    # def __init__(self,html=None):
    #     super().__init__(html)
    #     self.html=html

    def get_parse(self):
        return self.tree









if __name__=="__main__":
    xmlparser=XmlParser("sdfasdfaf")
    print(xmlparser)