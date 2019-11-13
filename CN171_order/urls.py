#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/2 0:26
# @Author: zhulong
# @File  : urls.py
# @Software: CN171


from django.conf.urls import url
from CN171_order import views as orderviews
from CN171_order import excelutils

urlpatterns = [

    #pboss order_status页面
    url(r'^pbossOrderStatus/', orderviews.pbossOrderStatus, name='pbossOrderStatus'),
    url(r'^pbossOrderStatusSearch/', orderviews.pbossOrderStatusSearch, name='pbossOrderStatusSearch'),
    url(r'^pbossOrderStatusMake/', orderviews.pbossOrderStatusMake, name='pbossOrderStatusMake'),

    #pboss order_node页面
    url(r'^pbossOrderNode/', orderviews.pbossOrderNode, name='pbossOrderNode'),
    url(r'^pbossOrderNodeSearch/', orderviews.pbossOrderNodeSearch, name='pbossOrderNodeSearch'),
    url(r'^pbossOrderNodeMake/', orderviews.pbossOrderNodeMake, name='pbossOrderNodeMake'),

    #pboss order_rollback页面
    url(r'^pbossOrderRollback/', orderviews.pbossOrderRollback, name='pbossOrderRollback'),
    url(r'^pbossOrderRollbackSearch/', orderviews.pbossOrderRollbackSearch, name='pbossOrderRollbackSearch'),
    url(r'^pbossOrderRollbackMake/', orderviews.pbossOrderRollbackMake, name='pbossOrderRollbackMake'),

    #pboss订单观察生成记录页面
    url(r'^pbossMakeRecord/', orderviews.pbossMakeRecord, name='pbossMakeRecord'),
    url(r'^pbossMakeRecordSearch/', orderviews.pbossMakeRecordSearch, name='pbossMakeRecordSearch'),
    url(r'^downloadRecordFile/', orderviews.downloadRecordFile, name='downloadRecordFile'),

]
