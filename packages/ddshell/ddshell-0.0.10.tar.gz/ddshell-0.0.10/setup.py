#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: mage
# Mail: mage@woodcol.com
# Created Time: 2018-1-23 19:17:34
#############################################


from setuptools import setup, find_packages

setup(
  name = "ddshell",
    version = "0.0.10",
  keywords = ("shell", "menu","ddshell", "ddmenu"),
  description = "shell菜单",
  long_description = "shell中的菜单，可以配置多级菜单，并执行",
  license = "MIT Licence",
  url = "https://gitee.com/chenddcoder/ddshell",
  author = "chenddcoder",
  author_email = "chenddcoder@foxmail.com",

  packages = find_packages(),
  include_package_data = True,
  platforms = "any",
  install_requires = [],
  entry_points={'console_scripts': [
    'ddshell = ddshell.dd:main'
  ]}
)