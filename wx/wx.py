from wxpy import *

#登陆
bot = Bot(cache_path=True)#扫码登陆微信，并且缓存账号信息
bot.file_helper.send('人生苦短我用python')#向文件传输助手发送消息


#实现自动回复一摸一样的信息。
# @bot.register()
# def print_message(msg):
#     print(msg.text)
#     return msg.text
# embed()


#定位群聊
# company_group = bot.groups().search('牛逼克拉斯')[0]
#
# # 定位老板
#
# boss = company_group.search('刘威')[0]
#
# # 将老板的消息转发到文件传输助手
# @bot.register(company_group)
# def forward_boss_message(msg):
#     if msg.member == boss:
#         msg.forward(bot.file_helper, prefix='老板发言')
#
# # 堵塞线程
# embed()

friends_stat = bot.friends().stats()
print(friends_stat)
friend_loc = [] # 每一个元素是一个二元列表，分别存储地区和人数信息
for province, count in friends_stat["province"].items():
    if province != "":
        friend_loc.append([province, count])
print(friend_loc)



#对人数倒序排序
friend_loc.sort(key=lambda x: x[1], reverse=True)

# 打印人数最多的10个地区
#绘图用
labels=[]
sizes=[]
for item in friend_loc[:10]:
    print(item[0], item[1])
    labels.append(item[0])
    sizes.append(item[1])

print(sizes,labels)
import matplotlib.pyplot as plt
import matplotlib as mpl  # 配置字体
plt.rcParams["font.sans-serif"] = ["cmb10"]
plt.rcParams['axes.unicode_minus'] = False


colors='lightgreen','gold','lightskyblue','lightcoral','lightgreen','gold','lightskyblue','lightcoral','lightskyblue','lightcoral'
explode=0.1,0.05,0.15,0.2,0.1,0.05,0.15,0.2,0.15,0.2
plt.pie(sizes,explode=explode,labels=labels,
        colors=colors,autopct='%1.1f%%',shadow=True,startangle=50)
plt.axis('equal')
plt.show()





