#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/11/21 11:10
# @Author: zhaocy
# @File  : my_tags.py.py
# @Software: CN171
import re

from django import template
register = template.Library()
@register.inclusion_tag("main-sidebar.html")
def get_menu_styles(request):
    permission_menu_dict = request.session.get("permission_menu_dict")
    print("permission_menu_dict", permission_menu_dict)

    for val in permission_menu_dict.values():
        for item in val["children"]:
            val["class"] = "hide"
            ret = re.search("^{}$".format(item["url"]), request.path)
            if ret:
                val["class"] = ""

    return {"permission_menu_dict": permission_menu_dict}

@register.filter
def has_permission(btn_url, request):
    permission_names = request.session.get("permission_names")
    return btn_url in permission_names

# 获取当前角色id，然后给url添加一个rid参数
@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params['rid'] = rid
    return params.urlencode()