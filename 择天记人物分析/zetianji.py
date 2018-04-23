import jieba
import pandas


#以下定义数据结构
names = {}            #姓名字典
relationships = {}    #关系字典
linenames = []        #每段内人物关系
all_names = []        #小说所有人物

#读取人名文件，并且存到小说所有人物关系列表alll_names中
f1 = open('/Users/tencenting/PycharmProjects/qm/venv/zetianji/names.txt',encoding='utf-8')
for line in f1.readlines():
    all_names.append(line.strip().strip('\ufeff'))#去除首位空格，并且移除首位非法字符
#以上得到所有小说所有人物all_name,并且添加人名到jieba词库中
for name in all_names:
    jieba.add_word(name)
print('本小说人物一共有',len(all_names),'人','人物列表:',all_names)

#统计小说人物出场人数模块
f2 = open('/Users/tencenting/PycharmProjects/qm/venv/zetianji/zetianji.txt',encoding='utf-8')
for line in f2.readlines():
    seg_list = jieba.cut(line) # 分词并返回该词词性
    linenames.append([]) # 为新读入的一段添加人物名称列表
    for i in seg_list:
        if i in all_names:
            linenames[-1].append(i) #为当前段的环境增加一个人物
            if names.get(i) is None:
                names[i] = 0
                relationships[i] = {}
            names[i] +=1  # 该人物出现次数加 1
# #观察人物出场次数
# for name, times in names.items():
#     print(name, times)

#人物关系
for line in linenames:       # 对于每一段
    for name1 in line:       # 每段中的任意两个人
        for name2 in line:
            if name1 == name2:
                continue
            if relationships[name1].get(name2) is None: # 若两人尚未同时出现则新建项
                relationships[name1][name2] = 1
            else:
                relationships[name1][name2] += 1        # 两人共同出现次数加 1
#数据写入部分
import codecs
import pandas as pd

with codecs.open("zej_node.txt", "w", "utf-8") as f:
    f.write("Id Label Weight\r\n")
    for name, times in names.items():
        f.write(name + " " + name + " " + str(times) + "\r\n")

with codecs.open("zej_edge.txt", "w", "utf-8") as f:
    f.write("Source Target Weight\r\n")
    for name, edges in relationships.items():
        for v, w in edges.items():
            if w > 3:
                f.write(name + " " + v + " " + str(w) + "\r\n")


print(names)
print(relationships)

