#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/11/20 17:36
# @Author: zhaocy
# @File  : setsession.py
# @Software: CN171
from CN171_account.models import Role


def initial_session(user_obj, request):
    """
    将当前登录人的所有权限url列表和
    自己构建的所有菜单权限字典和
    权限表name字段列表注入session
    :param user_obj: 当前登录用户对象
    :param request: 请求对象HttpRequest
    """
    # 查询当前登录人的所有权限列表
    ret = Role.objects.filter(user=user_obj).values('permissions__url',
                                                    'permissions__title',
                                                    'permissions__name',
                                                    'permissions__icon',
                                                    'permissions__menu__title',
                                                    'permissions__menu__icon',
                                                    'permissions__menu__classid',
                                                    'permissions__menu__url',
                                                    'permissions__menu__id').distinct()
    permission_list = []
    permission_names = []
    permission_menu_dict = {}
    for item in ret:
        # 获取用户权限列表用于中间件中权限校验
        permission_list.append(item['permissions__url'])
        # 获取权限表name字段用于动态显示权限按钮
        permission_names.append(item['permissions__name'])

        menu_pk = item['permissions__menu__id']
        if menu_pk:
            if menu_pk not in permission_menu_dict:
                permission_menu_dict[menu_pk] = {
                    "menu_title": item["permissions__menu__title"],
                    "menu_icon": item["permissions__menu__icon"],
                    'menu_classid':item['permissions__menu__classid'],
                    'menu_url':item['permissions__menu__url'],
                    "children": [
                        {
                            "title": item["permissions__title"],
                            "url": item["permissions__url"],
                            "icon": item["permissions__icon"]
                        }
                    ],
                }
            else:
                permission_menu_dict[menu_pk]["children"].append({
                    "title": item["permissions__title"],
                    "url": item["permissions__url"],
                })
    print('权限列表', permission_list)
    print('菜单权限', permission_menu_dict)
    # 将当前登录人的权限列表注入session中
    request.session['permission_list'] = permission_list
    # 将权限表name字段列表注入session中
    request.session['permission_names'] = permission_names
    # 将当前登录人的菜单权限字典注入session中
    request.session['permission_menu_dict'] = permission_menu_dict