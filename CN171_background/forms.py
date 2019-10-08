#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/9/30 9:43
# @Author: zhulong
# @File  : forms.py
# @Software: CN171

from django import forms
from django.forms.widgets import *

from .models import BgTaskLog,BgDomainStatusDict,BgTaskManagement

class BgForm(forms.ModelForm):
    class Meta:
        model = BgTaskManagement
        fields = ('bg_module','bg_domain','bg_task_start','bg_task_stop',
                  'bg_task_restart','bg_task_query')
        widgets = {
            'bg_module': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项，如 BES，CBS，VDS，Provision，Mediation'}),
            'bg_domain': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项，如 1，2，3，4'}),
            'bg_task_start': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'bg_task_stop': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'bg_task_restart': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'bg_task_query': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
        }

