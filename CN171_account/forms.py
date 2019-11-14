#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/11/12 14:29
# @Author: zhaocy
# @File  : forms.py
# @Software: CN171

from django import forms
from django.forms.widgets import *
from CN171_login.models import User


class accFrom(forms.ModelForm):
    class Meta:
        model = User
        fields = ('acc_user_name','acc_user_password','acc_user_CNname','acc_user_email',
                  'acc_role_name','acc_user_status')
        widgets = {
            'acc_user_name': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_password': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_CNname': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_email': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_role_name': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项，如 管理员,CMIOT运维, CMIOT运营,PBOSS运维,PBOSS运营'}),
            'acc_user_status': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;',
                                              'placeholder': u'必填项，如 启用，注销'}),

        }