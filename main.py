# -*- coding: utf-8 -*-
"""
@Time ： 2022/12/9 13:39
@Auth ： yuming
@File ：main.py
@IDE ：PyCharm
@Motto：A good song never tires of hearing a hundred times, a good book never tires of reading a hundred times
"""
from my_proxy_pool.settings import proxyfetcherSetting, checkSetting, mqSetting, CheckNum

"""采集代理池  
采集线程      存入queue    生产者
检测线程     从queue里 取proxy 测试 代理是否可用  可用的放入redis  消费者 
"""



from queue import Queue
queue=Queue(30)
def main():

    mq=mqSetting[0].get("cls")(mqSetting[0].get("streamName"))
    for proxyfetcher in proxyfetcherSetting:
        cls=proxyfetcher.get("cls")
        t=cls(name=proxyfetcher.get("name"),
              start_url=proxyfetcher.get("start_url"),
              times=proxyfetcher.get("times",10),
              next_lunci_sleep=proxyfetcher.get("next_lunci_sleep",60*60*6),
              mq=mq
              )
        t.start()

    for check in checkSetting:
        cls=check.get("cls")
        checkList=[]
        for i in range(0,CheckNum):
            group_name=f"group-{i}"
            for j in range(0,2):
                consumer_name=f"consumer-{j}"
                t=cls(hashTableName=check.get("hashTableName"),
                      mq=mq,
                      groupName=group_name,
                      consumerName=consumer_name,
                      streamName=mqSetting[0].get("streamName"))
                checkList.append(t)
        for t in checkList:
            t.start()



if __name__ == "__main__":
    main()