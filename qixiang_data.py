# -*- coding:UTF-8 -*-
'''
抓取每小时的 PM2.5 数据
python 3.6.5
url:http://www.pm25.in
'''
import os
import sys
import requests
from bs4 import BeautifulSoup
import csv
import time
import datetime

config_file = 'config'
url = 'http://www.pm25.in'

hour_second =  3600

# 表头数组
thead_arr=[]
# 表格数据数组
tbody_arr=[]
# 总数据数组
data_arr = []
#
index_city= {}

# 获取 gurl 对应的网页
def get_resquets(gurl):
    res = requests.get(gurl)
    return res
# 创建一个 res 的 html 文档对象
def create_beautifulsoup(res, t_parser):
    bf = BeautifulSoup(res.text, t_parser)
    return bf

#string:yyyymmddhhMMss 返回当前系统时间
def get_current_time ():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

# exists ture else false 判断 pfilename 路径是否存在
def check_file_exists(pfilename):
    return os.path.exists(pfilename)

# 返回一个储存 pfile 数据的字典
def paser_config (pfile):
    new_dict = {}
    new_arr = []
    # 以只读方式打开 pfile，并返回读取内容至 str
    f = open(pfile,'r')
    str = f.read()
    # 对 str 中每行数据分别赋值给 name 和 val ；再将 val 中的每项加入数组 new_arr
    # 在字典 new_dict 中添加一个键值对，key 为 name ，value 为加入 val 值的 new_arr
    # 最后清空 new_arr
    for item in str.split('\n'):
        name, val = item.split('=')
        for v in val.split(','):
            new_arr.append(v)

        new_dict[name]=new_arr
        new_arr = []
    return new_dict
#
def do_scrpy_data (dt_config):
    # 遍历 dt_config 中的 city
    for city in dt_config['city']:
        # 得到获取城市数据的 url 并打印
        city_url = url + '/' + city
        print(city_url)
        # 调用 get_city_data
        get_city_data(city, city_url)
        do_save_city(city)
        # 清空全局数组
        global data_arr
        global thead_arr
        data_arr=[]
        thead_arr=[]


def get_thead(tag):
    return tag.thead
def get_tbody(tag):
    return tag.tbody
# 获取 HTML 中所需数据的函数，注意里面所有子元素的名称都是通过对 HTML 结构进行人为浏览查看后得到的
def get_city_data(city, city_url):
    # 获取城市数据，并返回数据对象，其中 html.parser 在解析 HTML 文件时加上就好
    res = get_resquets(city_url)
    bf = create_beautifulsoup(res,'html.parser')
    # 提取所有 包含 table class 的 div，在网页中是整个数据表格的 div
    text = bf.find_all('div', class_='table')
    # 提取表格 HTML 中的 thead 子元素，它包含了表格的所有表头内容
    thead = get_thead(text[0])
    # 在 thead_arr 数组中加入 "地区时间" 四个字
    thead_arr.append('地区时间')
    # 遍历 HTML 表头的每个子元素，将所有 tr 子元素的内容放到 thead_arr 中
    # 这里只取了每个表头的第一个元素[0]，不影响结果
    for th in thead.tr.children:
        if th.name == 'th':
            thead_arr.append(str(th.contents[0]))

    # 提取表格 HTML 中的 tbody 子元素，它包含了表格的所有数据主体
    tbody = get_tbody(text[0])
    # 获得全局数组 tbody_arr
    global tbody_arr
    # 组合城市和当前时间
    c_t = city + get_current_time()
    # 遍历 HTML 每行数据的每个子元素，将所有 tr.td 子元素的内容放到 thead_arr 中
    for tr in tbody.children:
        if tr.name == 'tr':
            # 先加入自定义的第一行，记录城市和时间
            tbody_arr.append(c_t)
            # 对每个 td 子元素，获取其内容（因为 td 内部只有一个 NavigableString 类型子节点，所以使用 .string）
            for td in tr.children:
                if td.name =='td':
                    tstring = td.string
                    tbody_arr.append(tstring)
            # 向 data_arr 中加入包含本行所有表格数据的 tbody_arr，然后清空 tbody_arr，遍历下一行
            data_arr.append(tbody_arr)
            tbody_arr=[]
# 创建 path 文件夹
def mkdir(path):
    path=path.strip()
    path=path.rstrip("\\")

    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)

def do_save_city(city):
    # 定义生成的文件名，并查看该文件是否存在
    data_file = datetime.datetime.now().strftime('%Y-%m')
    city_file = "PM2.5 数据" + "\\" + city + "\\" + data_file
    mkdir(city_file)
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    filen = city_file + "\\" + date + '-' + city + '.csv'
    file_exists = check_file_exists(filen)
    # 以 a+ 模式打开文档（读写模式，没有该文件便创建，打开时文件为追加模式）
    # newline 参数可以保证 csv 写入数据时不会出现空行
    with open(filen, 'a+', newline='') as f:
        # 创建一个 csv writer，然后用 .writerow 写入数据
        writer = csv.writer(f)
        # 只要是新建文件，就插入表头
        if not file_exists:
            writer.writerow(thead_arr)
        # 逐行写入 data_arr 的数据
        for row in data_arr:
            #print(row)
            writer.writerow(row)

# return int
def get_interval_time (dt_config):
    return int(dt_config['flushTime'].pop())

if __name__ == "__main__":
    # 将 config 中的内容转化为数组 dt_config
    dt_config=paser_config(config_file)
    do_scrpy_data(dt_config)
