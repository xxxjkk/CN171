from django.shortcuts import render

from CN171_account.forms import accFrom
from CN171_account.service.setsession import initial_session
from CN171_background.api import pages, get_object
from django.http import HttpResponse, JsonResponse, FileResponse

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, HttpResponse
import re

from CN171_account.models import Role, User, Permission, Menu
from . import models
from .forms import UserForm

# Create your views here.

#用户管理主页面

#登录验证装饰器
def my_login_required(func):
    '''自定义 登录验证 装饰器'''
    def check_login_status(request, *args, **kwargs):
        '''检查登录状态'''
        if request.session.has_key('user_id'):
            # 当前有用户登录，正常跳转
            return func(request, *args, **kwargs)
        else:
            # 当前没有用户登录，跳转到登录页面
            return HttpResponseRedirect('/loginnotice')
    return check_login_status

#用户信息管理列表
def userManagement(request):
    user_List = models.User.objects.all()
    user_info_list = []
    for i in user_List:
        acc_user_name = i.acc_user_name
        acc_user_id = i.acc_user_id
        acc_user_CNname = i.acc_user_CNname
        acc_role_name = i.roles.all()[0].title
        acc_user_status = i.acc_user_status
        acc_user_createtime = i.acc_user_createtime
        acc_last_log_time = i.acc_last_log_time
        user_info = {"acc_user_id":acc_user_id,"acc_user_name":acc_user_name,"acc_user_CNname":acc_user_CNname,"acc_role_name":acc_role_name,"acc_user_status":acc_user_status,
                     "acc_user_createtime":acc_user_createtime,"acc_last_log_time":acc_last_log_time}
        user_info_list.append(user_info)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(user_info_list, request)
    return render(request, "account/user_management.html", locals())

#修改用户密码
def editPassword(request):
    if request.method == "POST":
        acc_user_id = request.session['user_id']
        user = models.User.objects.get(acc_user_id=acc_user_id)
        old_acc_user_password = request.POST['acc_user_password']
        if user.acc_user_password == old_acc_user_password :
            acc_user_password = request.POST['new_acc_user_password']
            user = models.User.objects.get(acc_user_id=acc_user_id)
            user.acc_user_password = acc_user_password
            try:
                user.save()
                returnmsg = "true"
                status = 1
                tips = u"修改成功！"
                display_control = ""
                request.session.flush()
            except:
                returnmsg = "false"
                status = 2
                tips = u"修改失败！"
                display_control = ""
        else:
            returnmsg = "false"
            status = 2
            tips = u"修改失败！"
            display_control = ""
        login_form = UserForm()
        return render(request, "login/login.html", locals())
    else:
        display_control = "none"
        return render(request, "account/password_edit.html", locals())

#添加用户
def userAdd(request):
    if request.method == "POST":
        acc_user_name = request.POST['acc_user_name']
        acc_user_password = request.POST['acc_user_password']
        acc_user_CNname = request.POST['acc_user_CNname']
        acc_user_email = request.POST['acc_user_email']
        acc_user_status = request.POST['acc_user_status']
        acc_role_name = request.POST['acc_role_name']
        role_name = Role.objects.get(title=acc_role_name)
        user = User()
        user.acc_user_name = acc_user_name
        user.acc_user_password = acc_user_password
        user.acc_user_CNname = acc_user_CNname
        user.acc_user_email = acc_user_email
        user.acc_user_status = acc_user_status
        user.save()
        user.roles.add(role_name)
        user.save()
        status = 1
        return render(request, "account/user_add.html", locals())
    else:
        display_control = "none"
        return render(request, "account/user_add.html", locals())


#删除用户
def userDel(request):
    acc_user_ids = request.POST.getlist('ids', [])
    returnmsg = "True"
    for acc_user_id in acc_user_ids:
        try:
            models.User.objects.filter(acc_user_id=acc_user_id).delete()
        except:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})

#编辑用户信息
def userEdit(request,acc_user_id):
    status = 0
    obj = get_object(models.User, acc_user_id = acc_user_id)

    if request.method == 'POST':
        accfrom = accFrom(request.POST, instance=obj)
        if accfrom.is_valid():
            accfrom.save()
            status = 1
        else:
            status = 2
    else:
        accform = accFrom(instance=obj)
    return render(request, 'account/user_edit.html', locals())

# 用户状态修改
def userStatusEdit(request):
    acc_user_id = request.POST.get('acc_user_id')
    nextStatus = request.POST.get('nextStatus')
    user = models.User.objects.get(acc_user_id=acc_user_id)
    if nextStatus == "enable":
       user.acc_user_status = "启用"
       returnmsg = "True"
    elif nextStatus == "disable":
       user.acc_user_status = "注销"
       returnmsg = "True"
    else:
        print("无效状态")
        returnmsg = "Flase"
    user.save()
    return JsonResponse({'ret': returnmsg})

# 用户信息搜索
def userSearch(request):
    acc_user_name = request.GET.get('acc_user_name')
    if acc_user_name == '':
        user_list = models.User.objects.all()
    else:
        user_list = models.User.objects.filter(acc_user_name=acc_user_name)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(user_list, request)
    return render(request, "account/user_management.html", locals())

def index(request):
    if request.session.get('is_login', None):
        temp_name = "navi-header.html"
        return render(request, "index.html", locals())
    else:
        # return redirect('/login')
        #提示未登陆，5秒后返回
        return render(request, "login/login_notice.html", locals())

#用户登录提示
def loginNotice(request):
    # 提示未登陆，5秒后返回
    return render(request, "login/login_notice.html", locals())

# 用户登录
def login(request):
    if request.session.get('is_login', None):
        return redirect('/index')
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(acc_user_name=username)
                if user.acc_user_password == password and user.acc_user_status == "启用":
                    initial_session(user,request)
                    request.session['is_login'] = True
                    request.session['user_id'] = user.acc_user_id
                    request.session['user_name'] = user.acc_user_name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())

# 用户注销登录
def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')

#用户角色权限管理
def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    # 用户id
    uid = request.GET.get('uid')
    # 角色id
    rid = request.GET.get('rid')

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        # 角色分配
        user = User.objects.filter(acc_user_id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        # 为用户分配角色
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        # 为角色分配权限，点中角色才能分配权限
        role = Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        # 为角色分配权限
        role.permissions.set(request.POST.getlist('permissions'))

    # 获取所有的用户
    user_list = User.objects.all()

    # 当前选中用户所拥有的角色
    user_has_roles = User.objects.filter(acc_user_id=uid).values('acc_user_id', 'roles')

    user_has_roles_dict = {item['roles']: None for item in user_has_roles}
    """
       user_has_roles_dict = { 角色的id：None  } 
       """
    # 所有的角色
    role_list = Role.objects.all()

    if rid:
        # 查出当前角色所拥有的权限
        role_has_permissions = Role.objects.filter(id=rid).values('id', 'permissions')
    elif uid and not rid:
        user = User.objects.filter(acc_user_id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        # 查出前用户所拥有的角色所对应的权限
        role_has_permissions = user.roles.values('id', 'permissions')
    else:
        role_has_permissions = []

    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}
    """"
       role_has_permissions_dict = { 权限的id ：None  }
       """

    all_menu_list = []
    """
        all_menu_list  = [   
            { 'id', 'title'， ‘children' : [  
                { 'id', 'title', 'menu_id' , 'children': [
                {'id', 'title', 'parent_id'}
            ] }
               ]   },
            {'id': None, 'title': '其他', 'children': [
             {'id', 'title', 'parent_id'}
            ]}
        ]
        """
    queryset = Menu.objects.values('id', 'title')
    menu_dict = {}
    """
        需要构成的分级数据结构
        menu_dict = { 一级菜单的id ： { 'id', 'title'， 
        ‘children' : [    
            { '二级菜单id', 'title', 'menu_id' , 'children': [
                {'id', 'title', 'parent_id'}
            ] }
         ]   },
            # 其他
             None : {'id': None, 'title': '其他', 'children': [
               {'id', 'title', 'parent_id'}
             ]}

        }
        """
    for item in queryset:
        item['children'] = []  # 放二级菜单  父权限
        menu_dict[item['id']] = item
        all_menu_list.append(item)

    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other

    # 二级菜单  父权限
    root_permission = Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')
    # 构建二级菜单权限数据结构
    root_permission_dict = {}
    """
      root_permission_dict =  { 父权限的id: { 'id', 'title', 'menu_id' , 'children': [
            {'id', 'title', 'parent_id'}
        ] }  }
        """
    for per in root_permission:
        per['children'] = []  # 放子权限
        nid = per['id']
        menu_id = per['menu_id']
        root_permission_dict[nid] = per
        menu_dict[menu_id]['children'].append(per)

    # 除了父权限的其他的权限
    node_permission = Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')
    # 构建其他权限的数据结构
    for per in node_permission:
        pid = per['parent_id']
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per)

    return render(
        request,
        'account/distribute_permission.html',
        {
            'user_list': user_list,
            'role_list': role_list,
            'user_has_roles_dict': user_has_roles_dict,
            'role_has_permissions_dict': role_has_permissions_dict,
            'all_menu_list': all_menu_list,
            'uid': uid,
            'rid': rid
        }
    )


#新增角色
def roleAdd(request):
    if request.method == "POST":
        title = request.POST.get('title')
        role = Role()
        role.title = title
        try:
            role.save()
            returnmsg = "true"
            status = 1
            tips = u"新增成功！"
            display_control = ""
        except:
            returnmsg = "false"
            status = 1
            tips = u"新增失败！"
            display_control = ""
        return render(request, "account/role_add.html", locals())
    else:
        display_control = "none"
        return render(request, "account/role_add.html", locals())

# 删除角色
def roleDel(request):
    ids = request.POST.getlist('ids', [])
    returnmsg = "true"
    for id in ids:
        role = models.Role.objects.get(id=id)
        user = role.user_set.all()
        if user:
            returnmsg = "False"
        else:
            role.delete()
            returnmsg = "true"
    return JsonResponse({'ret': returnmsg})

#新增权限
def permissionAdd(request):
    if request.method == "POST":
        url = request.POST.get('url')
        title = request.POST.get('title')
        name = request.POST.get('name')
        menu = request.POST.get('menu')
        parent = request.POST.get('parent')
        permission = Permission()
        permission.title = title
        permission.url = url
        permission.name = name
        if menu:
            permission_menu = models.Menu.objects.get(title=menu)
            permission.menu = permission_menu
        if parent:
            permission_parent = models.Permission.objects.get(title=parent)
            permission.parent = permission_parent
        try:
            permission.save()
            returnmsg = "true"
            status = 1
            tips = u"新增成功！"
            display_control = ""
        except:
            returnmsg = "false"
            status = 2
            tips = u"新增失败！"
            display_control = ""
        return render(request, "account/permission_add.html", locals())
    else:
        display_control = "none"
        return render(request, "account/permission_add.html", locals())

#删除权限
def permissionDel(request):
    ids = request.POST.getlist('ids', [])
    returnmsg = "true"
    for id in ids:
        permission = models.Permission.objects.get(id=id)
        role = permission.role_set.all()
        parent = models.Permission.objects.filter(parent = permission)
        if role or parent:
            returnmsg = "False"
        else:
            permission.delete()
            returnmsg = "true"
    return JsonResponse({'ret': returnmsg})