#!/usr/bin/env python
#-*- coding:utf-8 -*-
#############################################
# File Name: dd.py
# Author: chenddcoder
# Mail: chenddcoder@foxmail.com
# Created Time: 2023-02-17 14:38:00
#############################################
# （1）启动后读取配置文件，加载命令并展示
# （2）:e可编辑配置文件，编辑完后:qw退出（实际上用了vi工具）
# （3）配置文件格式tag=value形式，例如（查看cpu使用率=ps aux)
# （4）\结尾可以拼接下一行，#号可以写注释
# （5) 指令可配置默认脚本文件__SH__，“编号e“可以编辑默认脚本文件，脚本文件名称固定为路径.sh
import re
import os
import ddshell.utils as utils
def main():
    confPath = os.path.expanduser('~')+"/.ddshell"  # 全局路径，初始路径
    path=confPath
    menu = utils.showmenu(path)
    while True:
        a = input("请选择：")
        if a == "e":
            os.system("vi " + utils.menuconf(path))
        elif re.match(r'^\d+e$', a):
            # 匹配数字后跟e的输入
            num = int(a[:-1])  # 去掉最后一个字符e
            script_path = path + "/" + str(num) + ".sh"
            os.system(f"vi {script_path}")
            os.system(f"chmod +x {script_path}")
        elif a == "m":
            print("列出所有菜单")
            menu = utils.showmenu(path)
        elif a == "q":
            if path == confPath:
                break
            path = utils.predir(path)
            menu = utils.showmenu(path)
        elif a.isdigit():
            num = int(a)  # 菜单编号
            if num < len(menu):
                v = menu[num][1]  # 取菜单值,>表示进入子菜单
                if v.startswith(">"):
                    sub = v[1:]
                    path = utils.subdir(path, sub)
                    menu = utils.showmenu(path)
                else:
                    #如果是__SH__执行脚本文件
                    v=v.replace("__SH__",path +"/"+str(num)+".sh")
                    # print("执行脚本："+v)
                    os.system(v)
            else:
                print("无此选项")
                menu = utils.showmenu(path)
        else:
            print("无效操作")

if __name__ == '__main__':
    main()