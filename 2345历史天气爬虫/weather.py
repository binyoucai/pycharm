# -*- coding:utf-8 -*-
'''
The data of:2018/03/16
author:挖掘机大王子
content:爬取2345天气 全国历史天气数据 最多爬8年的天气数据
Last update time:2018/04/03
version:1.0
'''
#导入模块
from config import *             #导入配置文件
import os                        #文件系统模块
import requests                  #网络请求模块
import re                        #正则表达式模块
import  time                     #时间模块
import datetime                  #时间日期模块
from openpyxl import Workbook    #excel模块
from multiprocessing import Pool #多进程模块

#抓包分析
#从2011年到2016年采用老pai，2017年开始采用新的api
#http://tianqi.2345.com/t/wea_history/js/60231_20111.js
#http://tianqi.2345.com/t/wea_history/js/201701/60231_201701.js
#两个api的规律为:
# 2011-2016: http://tianqi.2345.com/t/wea_history/js/城市id_年月.js  其中年月格式为:年份+整数月份          比如 二零一零年一月份为：20111
# 2017-未来：http://tianqi.2345.com/t/wea_history/js/年月/城市id_年月.js   其中 年月格式为 年份+带序号的月份 比如二零零七年一月份为：201701
#实现思路：第一步构造请求url，得到数据之后进行处理，最后保存到excel


count=0 #计数，防止断网、网络突然中断、网络延迟而获取不到数据等情况。


#获取每一个月历史天气函数
def getEveryMonthWeatherList(cityCode,date,Mcount=count):
    global count
    try:
        api_data_1 = str(date.split('-')[0])+ str(int(date.split('-')[1]))
        api_data_2=str(date.split('-')[0])+str(date.split('-')[1])
        api_1_url = 'http://tianqi.2345.com/t/wea_history/js/{}_{}.js'.format(cityCode,api_data_1)            #年份<2017的api
        api_2_url = 'http://tianqi.2345.com/t/wea_history/js/{}/{}_{}.js'.format(api_data_2,cityCode, api_data_2)  #年份>=2017的api
        headers = {'user-agent': UA}       #http请求头
        try:
            response = requests.get(api_1_url, headers=headers) #先用api_1_url请求
            if response.status_code == 200:                    #如果年份小于2017则请求成功，否则访问失败，状态码不等于200,进入if语句
                print('原始数据地址==>', api_1_url, '请求成功\n开始处理数据')
                pattern = r'var weather_str=(.*?),{}]'  # 提取数据规则
                newPattern = re.compile(pattern, re.S)  # 提高效率匹配
                myAllList = re.findall(newPattern, response.text)[0]  # findall得到一个列表，取第一个元素 得到一个字典格式的数据
                secondP = r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)'"  # 提取数据规则
                newList = re.compile(secondP, re.S).findall(myAllList)
                print(len(newList), newList)
                return newList

            elif response.status_code != 200:                    #如果年份大于2016则请求失败，状态码不等于200,进入elif语句，尝试第二个api_2_url
                print( '大于2016年份，程序正在请求新api_2_url')
                response = requests.get(api_2_url, headers=headers)   #重新请求数据
                if response.status_code == 200:  # 请求成功之后，开始处理数据
                    print('原始数据地址==>',api_2_url, '请求成功\n开始处理数据')
                    pattern = r'var weather_str=(.*?),{}]'  # 提取数据规则
                    newPattern = re.compile(pattern, re.S)  # 提高效率匹配
                    myAllList = re.findall(newPattern, response.text)[0]  # findall得到一个列表，取第一个元素 得到一个字典格式的数据
                    secondP = r"ymd:'(.*?)',bWendu:'(.*?)',yWendu:'(.*?)',tianqi:'(.*?)',fengxiang:'(.*?)',fengli:'(.*?)',aqi:'(.*?)',aqiInfo:'(.*?)'"  # 提取数据规则
                    newList = re.compile(secondP, re.S).findall(myAllList)
                    print(len(newList), newList)
                    return newList
            else:
                print('可能输入日期有误')
                return None
        except Exception as e:                                        #确保程序将捕获除了系统退出事件之外的所有异常
            print('程序错误',e,'请检查年份是否超出范围')
    except Exception as e:   #确保程序将捕获除了系统退出事件之外的所有异常
        count+=1
        print(e,'第\t%d次\t请求链接出现问题，正在请求下一次链接......'%count)
        if count<10:
            getEveryMonthWeatherList(cityCode, date, Mcount=count)
        else:
            count = 0
            print('出错次数达到上限，程序结束，请检查函数 ')
            return None



#获取每个月的历史天气函数
def manyDateDataList(cityCode):
    try:
        dateList = createDateList(startDate,endDate)
        bigDataList = [] #新建一个保存天气数据的列表
        for date in dateList:
            try:
                smallList=getEveryMonthWeatherList(cityCode, date)
                print(smallList)
                bigDataList += smallList
            except Exception as e: #确保程序将捕获除了系统退出事件之外的所有异常
                print(e, 'error')
                continue
            time.sleep(1)
        print(len(bigDataList),bigDataList)
        return bigDataList
    except Exception as e:   #确保程序将捕获除了系统退出事件之外的所有异常
        print(e)


#写入excel函数，2017年开始有空气指数，空气质量指标
def write_excel_1(cityInfoList,cityCode):
    try:
        curCity = weatherCodeCity[cityCode]    #取出城市名称
        print('开始保存\t%s\t城市数据.....'%curCity)
        AllExcelHead = ['日期', '最高气温', '最低气温', '天气', '风向','风力', '空气指数','空气质量'] #定义excel工作簿列标题
        filePath=r'{}/{}'.format(SavePath, str(curCity))
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        doc = r'{}/{}{}_{}.{}'.format(filePath, curCity,startDate,endDate, 'xlsx')#保存在本地的地址，在config.py配置
        wb = Workbook()# 在内存创建一个工作簿obj
        ws=wb.active
        ws.title = curCity#给sheet重命名
        ws.append(AllExcelHead)
        k = 0 #写入计数
        for line in cityInfoList:
            try:
                print(line)
                ws.append(line)
                k += 1
                print('写入第%d条记录完毕' % (k))
            except Exception as e:   #确保程序将捕获除了系统退出事件之外的所有异常
                print(e,'第%d条记录有问题，已经忽略' % k)
                continue
        else:
            print('记录写入完成了，正在保存工作簿')
        wb.save(doc)
        print('\t{}\t城市数据保存完毕,文件路径是\t{}'.format(curCity,doc))
    except Exception as e:        #确保程序将捕获除了系统退出事件之外的所有异常
        print(e ,'函数 \twrite_excel_1\t出现问题了')
        pass


#写入excel函数，2017年前无，有空气指数，空气质量指标
def write_excel_2(cityInfoList,cityCode):
    try:
        curCity = weatherCodeCity[cityCode]    #取出城市名称
        print('开始保存\t%s\t城市数据.....'%curCity)
        AllExcelHead = ['日期', '最高气温', '最低气温', '天气', '风向','风力'] #定义excel工作簿列标题
        # 从城市编码反过来 得到城市名字

        print(curCity,'============================---------------')
        filePath=r'{}/{}'.format(SavePath, str(curCity))
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        # fetchDate = time.strftime("%Y-%m-%d", time.localtime())
        doc = r'{}/{}{}_{}.{}'.format(filePath, curCity,startDate,endDate, 'xlsx')#保存在本地的地址，在config.py配置
        wb = Workbook()# 在内存创建一个工作簿obj
        ws=wb.active
        ws.title = curCity#给sheet重命名
        ws.append(AllExcelHead)
        k = 0 #写入计数
        for line in cityInfoList:
            try:
                print(line)
                ws.append(line)
                k += 1
                print('写入第%d条记录完毕' % (k))
            except Exception as e:   #确保程序将捕获除了系统退出事件之外的所有异常
                print(e,'第%d条记录有问题，已经忽略' % k)
                continue
        else:
            print('记录写入完成了，正在保存工作簿')
        wb.save(doc)
        print('\t{}\t城市数据保存完毕,文件路径是\t{}'.format(curCity,doc))
    except Exception as e:        #确保程序将捕获除了系统退出事件之外的所有异常
        print(e ,'函数 \twrite_excel_1\t出现问题了')
        pass

#以下函数简单说明
#函数功能，输入起始日期和终止日期，得到起始日期-终止日期的列表，目的是为了构造请求url.
#比如输入startDate='2011-09'endDate='2011-12'得到 ['2011-09','2011-10','2011-11','2011-12']
#思路:1.利用split将开始年份和开始月份进行分离出来，2.利用列表生成器生成起始年份到终止年份的列表。3、2层循环写入年份和月份，外层为年份，内层为月份。注意循环终止条件。

#构造日期列表函数 
def createDateList(startDate,endDate):
    try:
        allDateList = []  # 新建一个列表保存日期
        startYear = int(startDate.split('-')[0])   # 开始年份
        startMonth = int(startDate.split('-')[1])  # 开始月份
        endYear = int(endDate.split('-')[0])       # 终止年份
        #endMonth = int(endDate.split('-')[1])      # 终止月份
        yearList = [year for year in range(int(startYear),int(endYear)+1)]           #生成起始年份和终止年份的列表
        monthList=['01','02','03','04','05','06','07','08','09','10','11','12']      #构造月份列表
        for year in yearList:
            tempList=[]  #新建一个列表保存日期，中间变量
            # 做判断，保证起始年份的起始月是对的
            if year==startYear:
                newMonthList=monthList[startMonth-1:]
            else:
                newMonthList=monthList

            for month in newMonthList:
                tempList.append('{}-{}'.format(year,month))
                yearMonth = '{}-{}'.format(year, month)  #记录写入当前日期
                if endDate == yearMonth:
                    break                     #记录写入当前日期，与终止日期进行比较，若相等则退出循环。此时外层循环迭代到最后一个年份了
            allDateList+=tempList             #把每次得到的日期都保存起来
        print(len(allDateList),allDateList)
        return allDateList
    except Exception as e:                         #确保程序将捕获除了系统退出事件之外的所有异常
        print(e,'创建日期列表出错了,这里只查询了 开始和结束日期....')
        return [startDate,endDate]


#获取城市id函数
def fromCityGetCityCode(needCityList):
    cityCodeLs=[]
    try:
        for curCity in needCityList:
            try:
                cityCode = weatherCityCode[curCity] # weatherCityCode 是一个字典 在config.py文件中，存放城市和编码的字典
                cityCodeLs.append(cityCode)  #保存代码，添加到列表
            except Exception as e:  #确保程序将捕获除了系统退出事件之外的所有异常
                print('不存在这样的城市名称',e,'你输入的城市名称错误,或配置文件不存在这样的城市，请输入中国城市名称.')
                continue
        return cityCodeLs          #返回城市id列表
    except Exception as e:         #确保程序将捕获除了系统退出事件之外的所有异常
        print(e,'从城市名字获取城市编码出错了')
        return None

#主函数
def main(cityCode):
    global endDate
    print(endDate)
    #得到一个城市 给定日期范围的 所有天气数据
    cityInfoList= manyDateDataList(cityCode)
    #同步写入文件 以城市和日期命名的
    if int(endDate.split('-')[0]) >= 2017:
        write_excel_1(cityInfoList,cityCode=cityCode)
    else:
        write_excel_2(cityInfoList, cityCode=cityCode)

#配置基本变量,你可以在这里设置
start = datetime.datetime.now()
SavePath='{}'.format(ROOT_DIR) #配置保存路径，此处在config.py模块配置
startDate='2015-11'   #配置开始日期
endDate='2018-3'     #配置结束日期
needCityList=['吕梁']   #配置城市
#全国城市['合肥', '安庆', '亳州', '蚌埠', '滁州', '池州', '阜阳', '淮北', '北京', '重庆', '上海', '天津', '淮南', '黄山', '六安', '马鞍山', '宿州', '铜陵', '芜湖', '宣城', '福州', '钓鱼岛', '龙岩', '南平', '宁德', '莆田', '泉州', '三明', '厦门', '漳州', '兰州', '甘南', '陇南', '白银', '定西', '金昌', '酒泉', '嘉峪关', '临夏', '平凉', '庆阳', '天水', '武威', '张掖', '广州', '潮州', '东莞', '佛山', '河源', '惠州', '江门', '揭阳', '梅州', '茂名', '清远', '深圳', '汕头', '韶关', '汕尾', '阳江', '云浮', '珠海', '中山', '湛江', '肇庆', '南宁', '北海', '百色', '崇左', '防城港', '桂林', '贵港', '贺州', '河池', '柳州', '来宾', '钦州', '梧州', '玉林', '贵阳', '黔南', '黔东南', '安顺', '毕节', '六盘水', '黔西南', '铜仁', '遵义', '海口', '白沙', '保亭', '澄迈', '昌江', '儋州', '定安', '东方', '临高', '陵水', '乐东', '琼海', '琼中', '三亚', '三沙', '屯昌', '文昌', '万宁', '五指山', '石家庄', '保定', '承德市', '沧州', '衡水', '邯郸', '廊坊', '秦皇岛', '唐山', '邢台', '张家口', '郑州', '安阳', '鹤壁', '焦作', '济源', '开封', '洛阳', '漯河', '南阳', '濮阳', '平顶山', '三门峡', '商丘', '新乡', '许昌', '信阳', '周口', '驻马店', '哈尔滨', '大庆', '大兴安岭', '鹤岗', '黑河', '佳木斯', '鸡西', '牡丹江', '齐齐哈尔', '七台河', '双鸭山', '绥化', '伊春', '武汉', '鄂州', '恩施', '黄石', '黄冈', '荆州', '荆门', '潜江', '十堰', '随州', '神农架', '天门', '襄阳', '孝感', '咸宁', '仙桃', '宜昌', '长沙', '湘西', '常德', '郴州', '衡阳', '怀化', '娄底', '黔阳', '邵阳', '湘潭', '岳阳', '益阳', '永州', '株洲', '张家界', '长春', '白山', '白城', '吉林', '辽源', '四平', '松原', '通化', '延边', '南京', '常州', '淮安', '连云港', '南通', '苏州', '宿迁', '泰州', '无锡', '徐州', '盐城', '扬州', '镇江', '南昌', '抚州', '赣州', '九江', '景德镇', '吉安', '萍乡', '上饶', '新余', '鹰潭', '宜春', '沈阳', '鞍山', '本溪', '朝阳', '大连', '丹东', '抚顺', '阜新', '葫芦岛', '锦州', '辽阳', '盘锦', '铁岭', '营口', '呼和浩特', '乌兰察布', '锡林郭勒', '阿拉善盟', '包头', '赤峰', '鄂尔多斯', '呼伦贝尔', '巴彦淖尔', '通辽', '乌海', '兴安盟', '银川', '固原', '石嘴山', '吴忠', '中卫', '西宁', '共和', '海西', '平安', '果洛', '海北', '黄南', '海东', '海南', '玉树', '济南', '滨州', '东营', '德州', '菏泽', '济宁', '莱芜', '临沂', '聊城', '青岛', '日照', '泰安', '潍坊', '威海', '烟台', '淄博', '枣庄', '太原', '长治', '大同', '晋城', '晋中', '临汾', '吕梁', '朔州', '忻州', '阳泉', '运城', '西安', '安康', '宝鸡', '汉中', '商洛', '铜川', '渭南', '咸阳', '延安', '榆林', '杨凌', '成都', '阿坝', '巴中', '德阳', '达州', '广元', '广安', '甘孜', '泸州', '乐山', '凉山', '绵阳', '眉山', '内江', '南充', '攀枝花', '遂宁', '宜宾', '雅安', '自贡', '资阳', '拉萨', '阿里', '昌都', '林芝', '那曲', '日喀则', '山南', '乌鲁木齐', '巴州', '克州', '伊犁', '阿克苏', '阿勒泰', '阿拉尔', '博州', '巴音郭楞', '博尔塔拉', '昌吉', '哈密', '和田', '克拉玛依', '喀什', '石河子', '吐鲁番', '塔城', '图木舒克', '铁门关', '五家渠', '昆明', '迪庆', '西双版纳', '保山', '楚雄', '大理', '德宏', '红河', '丽江', '临沧', '怒江', '普洱', '曲靖', '思茅', '文山', '玉溪', '昭通', '杭州', '湖州', '嘉兴', '金华', '丽水', '宁波', '衢州', '绍兴', '台州', '温州', '舟山']
# createDateList(startDate,endDate)

if __name__ == '__main__':
    cityCodeLs = fromCityGetCityCode(needCityList) #传入城市名称，获取城市代码
    pool = Pool()                 #创建多进程
    pool.map(main, cityCodeLs)    #开始多进程,等待任务完成
    end = datetime.datetime.now() #进程结束之后立即记录当前时间
    print('任务完成，消耗了 %s ' % (end - start))

