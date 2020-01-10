#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/17 10:07
# @Author: zhulong
# @File  : form.py
# @Software: CN171

from django import forms
from .models import OprFinanceFiledetail

#账务文件上传页面
class cFinanceMgntUploadForm(forms.Form):
    finance_file = forms.FileField(label=u'请选择需要上传的账务文件（支持 .zip、.unl.gz 格式）',
                                   error_messages={'required':'请选择需要上传的账务文件'})

