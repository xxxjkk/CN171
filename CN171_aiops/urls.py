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
    url(r'^capacityDetect/', aiopsviews.capacityDetect, name='capacityDetect'),
    url(r'^resultEcharts/(?P<id>\d+)/$', aiopsviews.resultEcharts, name='resultEcharts'),
    url(r'^warningpboss/', aiopsviews.warningPboss, name='warningPboss'),
    url(r'^resultSearch/', aiopsviews.resultSearch, name='resultSearch'),
    url(r'^warningPbossUpdateNum/', aiopsviews.warningPbossUpdateNum, name='warningPbossUpdateNum'),
    url(r'^warningPbossUpdateKpi/', aiopsviews.warningPbossUpdateKpi, name='warningPbossUpdateKpi'),
    url(r'^warningPbossUpdateAnalysis/', aiopsviews.warningPbossUpdateAnalysis, name='warningPbossUpdateAnalysis'),
    url(r'^warningDetail/', aiopsviews.warningDetail, name='warningDetail'),
]