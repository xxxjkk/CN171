#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/13 18:50
# @Author: zhulong
# @File  : urls.py
# @Software: CN171

from django.conf.urls import url
from CN171_aiops import views as aiopsviews

urlpatterns = [

    #智能运维页面
    url(r'^capacity/', aiopsviews.capacity, name='capacity'),
    url(r'^warningpboss/', aiopsviews.warningPboss, name='warningpboss'),
]