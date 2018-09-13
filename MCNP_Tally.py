#!/usr/bin/python
# -*- coding: UTF-8 -*-
from tkinter import filedialog
import os
import re

class RMC_Tally(object):
    def __init__(self, bin=[],total_AVE='',total_RE='',bin_AVE=[],bin_RE=[],type='',cell_id='',volume=[]):
        self.bin=bin
        self.total_AVE=total_AVE
        self.total_RE = total_RE
        self.bin_AVE=bin_AVE
        self.bin_RE=bin_RE
        self.type=type
        self.cell_id=cell_id
        self.volume = volume

    def get_bin(self):
        return self.bin
    def get_total_AVE(self):
        return self.total_AVE
    def get_total_RE(self):
        return self.total_RE
    def get_bin_AVE(self):
        return self.bin_AVE
    def get_bin_RE(self):
        return self.bin_RE
    def det_type(self):
        return self.type
    def get_cell_id(self):
        return self.cell_id
    def get_volume(self):
        return self.volume

def read_filename():
    file_dir=os.getcwd()
    filename = filedialog.askopenfilename(title='打开文件',initialdir=file_dir, filetypes=[('File', '*'), ('All Files', '*')])
    return filename

# 保存数据,可以保存能箱等
def save_data(ID_list,data=None):
    path=os.path.join(os.getcwd(),'MCNP_data')
    # 如果目录不存在，则创建目录
    if not os.path.exists(path):
        os.mkdir(path)
    for ID in ID_list:
        str = ''     # 如果str放到for循环的外面，后面文件包含前面文件内容
        filename = path + '\Tally' + ID + '.txt'
        try:
            for i in range(1,len(data[ID])):    # data[ID][0] 是 说明部分
                item=data[ID][i]
                str=str+item.get_total_AVE() + '\n'
            with open(filename, 'w') as f:
                f.write(str)
                f.close()
        except:
            pass

# 保存ID_list为以4结尾的栅元号
def save_total_AVE(ID_list,data=None):
    # path=os.path.join(os.getcwd(),'Total_AVE')
    # # 如果目录不存在，则创建目录
    # str=''
    # if not os.path.exists(path):
    #     os.mkdir(path)
    filename='Total_AVE.txt'
    str = ''
    for ID in ID_list:
        for i in range(1, len(data[ID])):
            item=data[ID][i]
            str= str + ''.join(item.get_total_AVE()).strip()  +  '\n'
    with open(filename, 'w') as f:
        f.write(str)
        f.close()

# 保存体积或质量数据，ID_list为以4结尾的栅元号
def save_volume(ID_list,data=None):
    path=os.path.join(os.getcwd(),'Volume')
    # 如果目录不存在，则创建目录
    str=''
    if not os.path.exists(path):
        os.mkdir(path)
    filename=path+'\Volume'+'.txt'
    for ID in ID_list:
        try:
            item=data[ID][0]
            str= str + '  '.join(item.get_volume()).strip()  +  '\n'
        except:
            pass
    with open(filename, 'w') as f:
        f.write(str)
        f.close()

# 查找一共有几个计数卡，并保存在read_mark与count_ID
def get_id_mark(filename):
    read_mark = []
    count_ID = []
    data_lines=''
    path = os.path.join(os.getcwd(), 'MCNP_data')
    # 如果目录不存在，则创建目录
    if not os.path.exists(path):
        os.mkdir(path)
    if filename:
        with open(filename, 'r') as f, open('data.txt', 'w+') as f2:
            ## 首先匹配1summary作为开始
            start_flag=False
            for line in f:
                start_compile=re.compile(r'1summary of photons(.*)', re.IGNORECASE)  # 1summary of photons...
                start_mark=start_compile.search(line)
                if start_mark:
                    start_flag=True
                if start_flag:
                    data_lines=data_lines+line
                    mark_compile = re.compile(r'(1tally \s*)(\d{1,})(.*)', re.IGNORECASE)  # 匹配ID
                    mark = mark_compile.search(line)
                    if mark:
                        count_ID.append(mark.group(2).strip())
                        read_mark.append(mark.group(0))
            # 保存 1summary of photons... 以后的数据
            f2.write(data_lines)
            f2.close()
            f.close()
    return read_mark,count_ID

def construct_data(paras=None):
    """
    construct surface using several lines
    """
    bin = []
    total_AVE = ''
    total_RE = ''
    volume = []
    bin_AVE = []
    bin_RE = []
    tally_list = []
    # paras check
    if not isinstance(paras, list):
        raise (ValueError, "paras must be a list")
    data_str = ''.join(paras)
    # 第一部分是说明部分，排除
    # 1tally  14        nps =100000000
    #            tally type 4    track length estimate of particle flux.      units   1/cm**2
    #            tally for  neutrons
    #
    #            volumes
    #                    cell:       3            6            9           11
    #                          1.32500E+04  1.92500E+04  3.47500E+04  8.17500E+04
    if '1tally' in data_str:
        flag=False
        bin = []
        total_AVE = ''
        total_RE = ''
        bin_AVE = []
        bin_RE = []
        type=''
        cell_id=''
        para_list = data_str.strip().split('\n')
        for item in para_list:
            if is_volume_start(item):
                flag=True
                continue
            if flag:
                if is_data_line(item):
                    volume.append(item.strip())
    else:
        para_list = data_str.strip().split('\n')
        tally_info=para_list[0]
        type=tally_info.strip().split()[0]
        try:
            cell_id = tally_info.strip().split()[1]
        except:             # 可能为 cell 这种情况，没有id
            cell_id ='a'
        for item in para_list:
            flag=is_data_line(item)
            if flag:
                tally_list.append(item)
        data_lines=len(tally_list)
        if data_lines > 1:
            # 获取计数
            total_AVE=tally_list[-1].strip().split()[-2]
            # 获取AVE
            total_RE=tally_list[-1].strip().split()[-1]
            for para in tally_list[0:-1]:
                # 获取能箱
                bin.append(para.strip().split()[0])
                # 获取计数
                bin_AVE.append(para.strip().split()[-2])
                # 获取AVE
                bin_RE.append(para.strip().split()[-1])
        elif data_lines == 1:
            # 获取计数
            total_AVE=tally_list[0].strip().split()[-2]
            # 获取AVE
            total_RE=tally_list[0].strip().split()[-1]
        else:
            pass
    return RMC_Tally(bin=bin,total_AVE=total_AVE,total_RE=total_RE,bin_AVE=bin_AVE,bin_RE=bin_RE,type=type,cell_id=cell_id,volume=volume)

def is_data_line(paras=None):
    flag = False
    pattern = re.compile(r'(\d+)?(\s+a?(total)?\s*\d{1,}\s*)(\.\d{1,})([E,e].?\d+)')
    mark = pattern.search(paras)
    if mark:
        flag = True
    return flag

def is_volume_start(paras=None):
    flag=False
    pattern = re.compile(r'\s{1,}cell:.*', re.IGNORECASE)
    search_mark = pattern.search(paras)
    if search_mark:
        flag = True
    return flag

def is_data_start(paras=None):
    flag = False
    pattern = re.compile(r'\s*cell.*',re.IGNORECASE) # 匹配       cell
    pattern1 = re.compile(r'\s*surface.*',re.IGNORECASE)  # 匹配         surface
    search_mark = pattern.search(paras)
    search_mark1 = pattern1.search(paras)
    # 排除 cell  a is (6830 6831 和 cell:     3    6    9    11
    if search_mark:
        if 'is'  in search_mark.group(0) or ':' in search_mark.group(0):
            flag = False
        else:
            flag = True
    if search_mark1:
        if 'is' in search_mark1.group(0) or ':' in search_mark1.group(0):
            flag = False
        else:
            flag = True
    return flag

def read_data( file,data_start_mark,data_end_mark):
    '''
    read data
    '''
    data = []
    pre_lines = []
    if file:
        data_start = False
        start_compile = re.compile(r'(.*)%s(.*)' % data_start_mark,re.IGNORECASE)  # 读取计数号，类似，1tally  14
        end_compile = re.compile(r'(.*)%s(.*)' % data_end_mark,re.IGNORECASE)
        for line in file:
            start_compile_mark = start_compile.search(line)
            end_compile_mark = end_compile.search(line)
            # read and treat
            if start_compile_mark:
                data_start = True
                # continue
            if data_start:
                if end_compile_mark:
                    data_line = construct_data(pre_lines)
                    data.append(data_line)
                    break
                # read data
                data_flag = is_data_start(line)  # 完成 cell  3 或 surface  41 的读取
                # # 如果不是数据行，跳过这行
                # if not is_data_line(line):
                #     continue
                if data_flag:
                    # lines in previous block represent a surface
                    if pre_lines:
                        data_line = construct_data(pre_lines)
                        data.append(data_line)
                        pre_lines = []
                    # store this line in the buffer
                    pre_lines.append(line)  #   读不读取  cell  3 或 surface  41
                else:
                    # this line is a data line, store in the buffer，continue line
                    pre_lines.append(line)
        return data