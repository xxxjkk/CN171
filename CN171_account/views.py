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

@my_login_required
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
        return render(request, "account/user_add.html", locals())
    else:
        display_control = "none"
        return render(request, "account/user_add.html", locals())


#添加用户
def userDel(request):
    acc_user_ids = request.POST.getlist('ids', [])
    returnmsg = "True"
    for acc_user_id in acc_user_ids:
        try:
            models.User.objects.filter(acc_user_id=acc_user_id).delete()
        except:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})

#编辑用户


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

# 启用用户

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

# 启用用户
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

def loginNotice(request):
    # 提示未登陆，5秒后返回
    return render(request, "login/login_notice.html", locals())

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


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session.flush()
    return redirect('/login/')


# def rolePermission(request):
#     roleList = models.Role.objects.all()
#     permission_list = []
#     for i in roleList:
#         role_id = i.id
#         permission_info_list = []
#         role_title = i.title
#         permission_List = i.permissions.all()
#         lenght = len(permission_List)
#         for j in permission_List:
#             permission_title = j.title
#             permission_info = {"permission_title":permission_title}
#             permission_info_list.append(permission_info)
#         role_info_list = {"role_title":role_title,"permission_info_list":permission_info_list}
#         permission_list.append(role_info_list)
#     p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(permission_list, request)
#     return render(request, "account/role_permission_management.html", locals())



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


# def register(request):
#     if request.session.get('is_login', None):
#         # 登录状态不允许注册。你可以修改这条原则！
#         return redirect("/index/")
#     if request.method == "POST":
#         register_form = RegisterForm(request.POST)
#         message = "请检查填写的内容！"
#         if register_form.is_valid():  # 获取数据
#             username = register_form.cleaned_data['username']
#             password1 = register_form.cleaned_data['password1']
#             password2 = register_form.cleaned_data['password2']
#             email = register_form.cleaned_data['email']
#             sex = register_form.cleaned_data['sex']
#             if password1 != password2:  # 判断两次密码是否相同
#                 message = "两次输入的密码不同！"
#                 return render(request, 'login/register.html', locals())
#             else:
#                 same_name_user = models.User.objects.filter(name=username)
#                 if same_name_user:  # 用户名唯一
#                     message = '用户已经存在，请重新选择用户名！'
#                     return render(request, 'login/register.html', locals())
#                 same_email_user = models.User.objects.filter(email=email)
#                 if same_email_user:  # 邮箱地址唯一
#                     message = '该邮箱地址已被注册，请使用别的邮箱！'
#                     return render(request, 'login/register.html', locals())
#
#                 # 当一切都OK的情况下，创建新用户
#
#                 new_user = models.User.objects.create()
#                 new_user.name = username
#                 new_user.password = password1
#                 new_user.email = email
#                 new_user.sex = sex
#                 new_user.save()
#                 return redirect('/login/')  # 自动跳转到登录页面
#     register_form = RegisterForm()
#     return render(request, 'login/register.html', locals())


#def hash_code(s, salt='mysite_login'):
#    h = hashlib.sha256()
#    s += salt
#    h.update(s.encode())  # update方法只接收bytes类型
#    return h.hexdigest()

