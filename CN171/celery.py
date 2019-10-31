#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/10 19:58
# @Author: zhulong
# @File  : celery.py
# @Software: CN171

from __future__ import absolute_import, unicode_literals
import os
import CN171_crontab
from celery import Celery

#设置django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CN171.settings')

app = Celery('CN171')

#使用CELERY_ 作为前缀，在settings中写配置
app.config_from_object('django.conf:settings')

#发现任务文件每个app下的task.py
app.autodiscover_tasks(['CN171_order.tasks', 'CN171_background.tasks'])