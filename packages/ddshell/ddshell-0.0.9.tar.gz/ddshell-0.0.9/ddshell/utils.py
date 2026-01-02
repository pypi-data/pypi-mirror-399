# -*- coding:utf-8 -*-
#############################################
# File Name: utils.py
# Author: chenddcoder
# Mail: chenddcoder@foxmail.com
# Created Time: 2023-02-17 14:38:00
#############################################
# 引入模块
import os
import re
# 创建文件夹
def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        # print(path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        # print(path+' 目录已存在')
        return False


# 读取配置文件，返回List<map>
def config(path):
    regex=re.compile(r"#[^'^\"]*$")
    print(path)
    mkdir(os.path.dirname(path))
    # 数组返回
    menuDem = []
    if not os.path.exists(path):
        return menuDem
    with open(path, "r+") as ff:
        oneLine = ""
        for tmpLine in ff.readlines():
            # 先删除注释，避免注释行被合并
            original_line = tmpLine.strip()
            if original_line.startswith("#"):  # 如果整行都是注释，直接跳过
                continue
            # 去掉#后面的文字
            tmpLine=regex.sub('',tmpLine)
            # 去掉2变空格
            tmpLine = tmpLine.strip()
            oneLine += tmpLine
            if tmpLine.endswith("\\"):  # 如果\结尾，拼接下一行
                continue
            if len(oneLine) == 0:  # 如果长度为0，忽略
                continue
            if oneLine.find("=")!=-1: #不含=忽略
                kv = oneLine.split("=", 2)
                menuDem.append(kv)
                oneLine = ""
        if len(oneLine) != 0:
            if oneLine.find("=")!=-1: 
                kv = oneLine.split("=", 2)
                menuDem.append(kv)
    return menuDem


# 返回拼接目录
def subdir(path, sub):
    return path + "/" + sub


# 返回上级目录
def predir(path):
    return path.rsplit("/", 1)[0]


def showmenu(path):
    menu = config(menuconf(path))
    showmenuV(menu, path)
    return menu


def showmenuV(m, path):
    os.system("clear")
    print("===============" + path + "================")
    print("===============高级操作：编号e可编辑脚本文件 配置指令__SH__可以执行对应脚本================")
    print("e:编辑")
    for i in range(len(m)):
        if (m[i][1]).startswith(">"):
            print(str(i) + " > " + m[i][0])
        else:
            print(str(i) + " : " + m[i][0])
    print("q:退出")


def menuconf(path):
    path = path.strip()
    return path + "/menu.conf"
