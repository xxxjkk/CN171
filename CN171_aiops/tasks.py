#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/12 15:26
# @Author: zhaocy
# @Time  : 2020/1/3
# @Author: liuyx
# @File  : tasks.py
# @Software: CN171

#调用celery中的task模块
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from CN171_aiops import excelutil, textutil

@shared_task
def excelReadWarning():
    print ("-----------启动excel读取task-----------")
    excelutil.excelRead()
    print ("-----------结束excel读取task-----------")

@shared_task
def textReadWarning():
    print ("-----------启动text读取task-----------")
    textutil.textRead()
    print ("-----------结束text读取task-----------")