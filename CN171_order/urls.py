#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/2 0:26
# @Author: zhulong
# @File  : urls.py
# @Software: CN171


from django.conf.urls import include,url
from CN171_order import views as orderviews

urlpatterns = [

    #pboss order主页面
    url(r'^pbossOrderStatus/', orderviews.pbossOrderStatus, name='pbossOrderStatus'),
    url(r'^pbossOrderStatusSearch/', orderviews.pbossOrderStatusSearch, name='pbossOrderStatusSearch'),
    url(r'^pbossOrderStatusMake/', orderviews.pbossOrderStatusMake, name='pbossOrderStatusMake'),

    url(r'^pbossOrderNode/', orderviews.pbossOrderNode, name='pbossOrderNode'),
    url(r'^pbossOrderRollback/', orderviews.pbossOrderRollback, name='pbossOrderRollback'),

    #pboss订单观察生成记录
    url(r'^pbossMakeRecord/', orderviews.pbossMakeRecordQuery, name='pbossMakeRecord'),

]
