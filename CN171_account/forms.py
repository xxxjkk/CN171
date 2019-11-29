#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/11/12 14:29
# @Author: zhaocy
# @File  : forms.py
# @Software: CN171

from django import forms
from django.forms.widgets import *
from CN171_account.models import User


class accFrom(forms.ModelForm):
    class Meta:
        model = User
        fields = ('acc_user_name','acc_user_password','acc_user_CNname','acc_user_email',
                  'acc_user_status')
        widgets = {
            'acc_user_name': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_password': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_CNname': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_email': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'acc_user_status': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;',
                                              'placeholder': u'必填项，如 启用，注销'}),

        }
class UserForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        max_length=128,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'}))
    password = forms.CharField(
        label="密码",
        max_length=256,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'}))
    #captcha = CaptchaField(label='验证码')


# class RegisterForm(forms.Form):
#     gender = (
#         ('male', "男"),
#         ('female', "女"),
#     )
#     username = forms.CharField(
#         label="用户名",
#         max_length=128,
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control'}))
#     password1 = forms.CharField(
#         label="密码",
#         max_length=256,
#         widget=forms.PasswordInput(
#             attrs={
#                 'class': 'form-control'}))
#     password2 = forms.CharField(
#         label="确认密码",
#         max_length=256,
#         widget=forms.PasswordInput(
#             attrs={
#                 'class': 'form-control'}))
#     email = forms.EmailField(
#         label="邮箱地址",
#         widget=forms.EmailInput(
#             attrs={
#                 'class': 'form-control'}))
#     sex = forms.ChoiceField(label='性别', choices=gender)
#     #captcha = CaptchaField(label='验证码')