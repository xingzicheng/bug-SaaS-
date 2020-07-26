#!/usr/bin/env python
# -*- coding:utf-8 -*-
# import os
# import sys
# import django
#
# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(base_dir)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bugsite.settings")
# django.setup()  # os.environ['DJANGO_SETTINGS_MODULE']
#
# print("我")
#from web import models
# 往数据库添加数据：链接数据库、操作、关闭链接
#models.UserInfo.objects.create(username='陈硕', email='chengshuo@live.com', mobile_phone='13838383838', password='123123')
# from xpinyin import Pinyin


# # 实例拼音转换对象
# p = Pinyin()
# # 进行拼音转换
# x = "文件夹S25"

# r = p.get_pinyin(x)
# print(r)
# print(r.lower())

# request.tracer的例子
class a:
    def __init__(self, *args, **kwargs):
        self.tra = 3
        self.x = b()

class b:
    def __init__(self, *args, **kwargs):
        self.name = 2

request = a()
print(request.tra)
request.tr = b()
print(request.tr)
print(request.tr.name)
print(request.x.name)
request.y = 4
print(request.y)
print(request)
