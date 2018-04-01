'''
time:2018 03 15
by:北冥神君
内容：爬取拉勾网python职位信息

'''

#导入模块
import requests #网络请求模块
import re #正则模块
import time #时间模块
import random #随机数模块
import pandas as pd

# post的网址
url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0'

# 反爬措施
header1 = {'Host': 'www.lagou.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Anit-Forge-Token': 'None',
        'X-Anit-Forge-Code': '0',
        'Content-Length': '26',
        'Cookie': 'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519816933,1519816935,1521079570,1521079575; _ga=GA1.2.129319102.1515420746; user_trace_token=20180108221226-f4036578-f47d-11e7-a021-5254005c3644; LGUID=20180108221226-f40369cf-f47d-11e7-a021-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1521081597; LGSID=20180315100701-8cabf3af-27f5-11e8-b1fc-525400f775ce; LGRID=20180315103956-2609450b-27fa-11e8-b1ed-5254005c3644; _gid=GA1.2.2023749020.1521079570; JSESSIONID=ABAAABAAAIAACBI02527B187B701F2E661E90B666E236AF; hideSliderBanner20180305WithTopBannerC=1; TG-TRACK-CODE=search_code; SEARCH_ID=c9472cb5ce184e00bf8dcd8989fdc892; _gat=1; X_HTTP_TOKEN=d5fd7e2b382eab92942c6aee48b65dfa',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'}
header2 = {'Host': 'www.lagou.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Anit-Forge-Token': 'None',
            'X-Anit-Forge-Code': '0',
            'Cookie': 'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1519816933,1519816935,1521079570,1521079575; _ga=GA1.2.129319102.1515420746; user_trace_token=20180108221226-f4036578-f47d-11e7-a021-5254005c3644; LGUID=20180108221226-f40369cf-f47d-11e7-a021-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1521081597; LGSID=20180315100701-8cabf3af-27f5-11e8-b1fc-525400f775ce; LGRID=20180315103956-2609450b-27fa-11e8-b1ed-5254005c3644; _gid=GA1.2.2023749020.1521079570; JSESSIONID=ABAAABAAAIAACBI02527B187B701F2E661E90B666E236AF; hideSliderBanner20180305WithTopBannerC=1; TG-TRACK-CODE=search_code; SEARCH_ID=c9472cb5ce184e00bf8dcd8989fdc892; _gat=1; X_HTTP_TOKEN=d5fd7e2b382eab92942c6aee48b65dfa',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'}

for n in range(1,31):
    # 要提交的数据
    form = {'first': 'false',
            'kd': 'Python',
            'pn': str(n)}

    time.sleep(random.randint(5, 10))#随机暂停5-10秒

    # 提交数据
    html = requests.post(url, data=form, headers=header1)

    # 提取数据
    data = re.findall(
        '{"companyId":.*?,"positionName":"(.*?)","workYear":"(.*?)","education":"(.*?)","jobNature":"(.*?)","financeStage":"(.*?)","companyLogo":".*?","industryField":".*?","city":"(.*?)","salary":"(.*?)","positionId":.*?,"positionAdvantage":"(.*?)","companyShortName":"(.*?)","district"',
        html.text)
    print(data)
    #提取公司ID
    companyId = re.findall(
        '{"companyId":(.*?),.*?,"district"',
        html.text)
    print(companyId)
    companyIds = ','.join(companyId)
    print(companyIds)
    urlcompanyUrl = 'https://www.lagou.com/c/approve.json?companyIds='+companyIds
    print(urlcompanyUrl)
    #反爬
    get_company = requests.get(url=urlcompanyUrl,headers = header2)
    print(get_company.text)

    # 转换成数据框

    data = pd.DataFrame(data)
    print(data)

    # 保存在本地
    data.to_csv(r'LaGouData.csv', header=False, index=False, mode='a+')