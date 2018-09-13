#!/usr/bin/python
# -*- coding: UTF-8 -*-

from MCNP_Tally import *

filename = read_filename()
# 获取计数号ID与栅元计数标记
read_mark,count_ID=get_id_mark(filename)
count_num=len(count_ID)
# 将数据保存在字典data中，键：ID号,值：RMC_Tally类
data={}


with open('data.txt', 'r') as f:   # 传入打开后饿文件，避免每次打开文件
    for i in range(count_num):
        data_start_mark=read_mark[i]
        data_end_mark='results of 10 statistical checks'
        data[count_ID[i]]=read_data( f,data_start_mark,data_end_mark)
    f.close()

# 检查MCNP_data目录下是否存在文件，若存在先清空
path=os.path.join(os.getcwd(),'MCNP_data')
if os.path.exists(path):
# 如果存在，则先清空
    file_list = [f for f in os.listdir(path) if f.endswith(".txt")]
    for f in file_list:
        os.remove(os.path.join(path,f))

# 删除data.txt文件,data.txt是1summary后面的内容
if os.path.exists('data.txt'):
    os.remove('data.txt')

# 保存数据的ID,Tally1,Tally4，Tally6
ID_list=[]
for i in range(len(data)):
    ID=count_ID[i]
    if ID.endswith('4'):  # Tally 4
        ID_list.append(ID)
# 保存数据,选择性保存
save_data(ID_list,data)
# 保存total_AVE
save_total_AVE(ID_list,data)
# 获取体积
save_volume(ID_list,data)

# # 将每个ID 的计数相加
# Total_count=[]
# for i in range(len(data)):
#     total=0.0
#     ID=count_ID[i]
#     for item in data[ID]:
#         total=total+float(item.get_total_AVE())
#     Total_count.append(total)
# # 将数字转化为字符串
# str=''
# for item in Total_count:
#     str=str+'{:.6}'.format(item)+'\n'
#
# with open('total.txt', 'w') as f:
#             f.write(str)
#             f.close()

#画图



