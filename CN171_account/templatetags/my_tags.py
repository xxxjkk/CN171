#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/11/21 11:10
# @Author: zhaocy
# @File  : my_tags.py.py
# @Software: CN171
import re
from collections import OrderedDict

from django import template
register = template.Library()
@register.inclusion_tag("main-sidebar.html")
def get_menu_styles(request):
    permission_menu_dict = request.session.get("permission_menu_dict")

    # 因为字典是无序的，要使菜单显示有序:
    # 1.在model的菜单表中设置weight权重字段，
    # 2.引用sorted()按权重排序倒叙，权重越大显示越靠前
    # 3.将数据放到有序字典中
    # sorted() 函数对所有可迭代的对象进行排序操作。
    # sort 是应用在 list 上的方法，sorted 可以对所有可迭代的对象进行排序操作。

    order_dict = OrderedDict()
    for i in sorted(permission_menu_dict, key=lambda x: permission_menu_dict[x]['menu_weight'], reverse=True):
        # 复制到order_dict中
        order_dict[i] = permission_menu_dict[i]
        # 取一级菜单的信息
        item = order_dict[i]
        for j in item["children"]:
            item["class"] = "hide"
            ret = re.search("^{}$".format(j["url"]), request.path)
            if ret:
                item["class"] = ""
    print(order_dict.values())
    return {"permission_menu_dict": order_dict}

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