'''
简单的查询12306车票爬虫程序
by:北冥
'''

import requests#网络请求模块
#数据获取模块
def getTrainInfo():
    response = requests.get('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2017-12-14&leftTicketDTO.from_station=CSQ&leftTicketDTO.to_station=CDW&purpose_codes=ADULT')
    return response.json()['data']['result']#dict

#数据分析过程
'''
车次的索引=3
出发时间索引=8
到达时间索引=9
历时索引=10
软卧索引=23
硬卧索引=28
硬座索引=29
二等座索引=30
一等座=31
特等座索引／商务座=32

'''
#票数判断模块
for i in getTrainInfo():
    tmp_list = i.split('|')
    if tmp_list[23] != "" and tmp_list[23] !=u'无':
        print(tmp_list[3])
        print(tmp_list[23])#打印剩余票数
