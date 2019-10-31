# -*-coding:utf-8 -*-
import os
import re
import sys
import threading

from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseRedirect
from CN171_background import models
from CN171_background.api import pages,get_object
from django.shortcuts import render, redirect

from CN171_background.forms import BgForm
from CN171_background.models import BgTaskManagement, BgTaskLog
from CN171_login.views import my_login_required
from django.db.models import Q
from datetime import datetime
from CN171_background import tasks

# Create your views here.
try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp
# 后台管理函数
from CN171_tools.connecttool import ssh_close, ssh_connect, ssh_exec_cmd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'))
conntarget = "Ansible"


@my_login_required
def taskManagement(request):
    # 获取所有后台对象
    # page_len = request.GET.get('page_len', '')
    task_list=[]
    keyword = request.GET.get("keyword","")
    if keyword:
        task_list=models.BgTaskManagement.objects.filter(
            Q(bg_module__icontains = keyword ) |
            Q(bg_domain__icontains = keyword ) |
            Q(bg_status__icontains = keyword)  |
            Q(bg_lastopr_user__icontains = keyword) |
            Q(bg_lastopr_type__icontains =keyword)  |
            Q(bg_lastopr_result__icontains= keyword)
        )
    else:
        task_list = models.BgTaskManagement.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(task_list, request)
    return render(request, "background/task_management.html", locals())


# 单个按钮执行函数
@my_login_required
def taskExecuteOne(request):
    bg_id = request.POST.get('bg_id')
    opr_user = request.session['user_name']
    bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
    bgTaskManagement.bg_status = "进行中"
    bgTaskManagement.save()
    bg_action = request.POST.get('bg_action')
    bg_log = BgTaskLog()
    bg_log.bg_id = bg_id
    bg_log.bg_operation_time = datetime.now()
    bg_log.bg_operation_user = opr_user
    bg_log.bg_opr_result = "待执行"
    # 写入日志文件
    bg_log.save()
    bg_log_id = bg_log.bg_log_id
    tasks.taskOne.delay(bg_id,bg_action,opr_user,bg_log_id)
    return JsonResponse({'ret': "True"})

# 批量启动按钮
@my_login_required
def batchTaskStart(request):
    bg_ids = request.POST.getlist('ids', [])
    opr_user = request.session['user_name']
    returnmsg = "true"
    bg_action = 'start'
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if  bgTaskManagement.bg_status=="停止":
            bgTaskManagement.bg_status = "进行中"
            bgTaskManagement.save()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = opr_user
            bg_log.bg_opr_result = "待执行"
            # 写入日志文件
            bg_log.save()
            bg_log_id = bg_log.bg_log_id
            tasks.taskOne.delay(bg_id,bg_action,opr_user,bg_log_id)
            returnmsg = "True"
        else:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})
    #return redirect("taskManagement")

#批量停止功能
@my_login_required
def batchTaskStop(request):
    bg_ids = request.POST.getlist('ids', [])
    returnmsg = "true"
    bg_action = 'stop'
    opr_user = request.session['user_name']
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if  bgTaskManagement.bg_status == "正常"or bgTaskManagement.bg_status == "部分正常" or bgTaskManagement.bg_status == "异常" :
            bgTaskManagement.bg_status = "进行中"
            bgTaskManagement.save()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = opr_user
            bg_log.bg_opr_result = "待执行"
            # 写入日志文件
            bg_log.save()
            bg_log_id = bg_log.bg_log_id
            tasks.taskOne.delay(bg_id,bg_action,opr_user,bg_log_id)
            returnmsg = "True"
        else:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})

# 批量重启
@my_login_required
def batchTaskReboot(request):
    bg_ids = request.POST.getlist('ids', [])
    returnmsg = "true"
    bg_action = 'restart'
    opr_user = request.session['user_name']
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if bgTaskManagement.bg_status == "正常" or bgTaskManagement.bg_status == "部分正常" or bgTaskManagement.bg_status == "异常":
            bgTaskManagement.bg_status = "进行中"
            bgTaskManagement.save()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = opr_user
            bg_log.bg_opr_result = "待执行"
            # 写入日志文件
            bg_log.save()
            bg_log_id = bg_log.bg_log_id
            tasks.taskOne.delay(bg_id, bg_action, opr_user,bg_log_id)
            returnmsg = "True"
        else:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})


# 批量刷新页面
@my_login_required
def reLoad(request):
    idlist = BgTaskManagement.objects.values_list('bg_id', flat=True)
    returnmsg = "true"
    bg_action = 'query'
    opr_user = request.session['user_name']
    for bg_id in idlist:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if bgTaskManagement.bg_status != "进行中":
            bgTaskManagement.bg_status = "进行中"
            bgTaskManagement.save()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = opr_user
            bg_log.bg_opr_result = "待执行"
            # 写入日志文件
            bg_log.save()
            bg_log_id = bg_log.bg_log_id
            tasks.taskOne.delay(bg_id, bg_action, opr_user,bg_log_id)
            returnmsg = "True"
        else:
            returnmsg = "False"
    return JsonResponse({'ret': returnmsg})

# 多线程创建函数
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None

#后台中心编辑函数
@my_login_required
def taskEdit(request, bg_id):
    status = 0
    obj = get_object(BgTaskManagement, bg_id=bg_id)

    if request.method == 'POST':
        bgform = BgForm(request.POST, instance=obj)
        if bgform.is_valid():
            bgform.save()
            status = 1
        else:
            status = 2
    else:
        bgform = BgForm(instance=obj)
    return render(request, 'background/task_edit.html', locals())

#后台中心添加函数
@my_login_required
def taskAdd(request):
    status = 0
    if request.method == "POST":
        bgform = BgForm(request.POST)
        if bgform.is_valid():
            bgform.save()
            status = 1
            tips = u"新增成功！"
            display_control = ""
        else:
            status = 2
            tips = u"新增失败！"
            display_control = ""
        return render(request, "background/task_add.html", locals())
    else:
        display_control = "none"
        bgform = BgForm()
        return render(request, "background/task_add.html", locals())

#后台中心删除函数
@my_login_required
def taskDel(request):
    bg_id = request.GET.get('bg_id', '')
    if bg_id:
        BgTaskManagement.objects.filter(bg_id=bg_id).delete()

    if request.method == 'POST':
        bg_batch = request.GET.get('arg', '')
        bg_id_all = str(request.POST.get('bg_id_all', ''))

        if bg_batch:
            for bg_id in bg_id_all.split(','):
                bg_item = get_object(BgTaskManagement, bg_id=bg_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')

#后台日志展示界面
@my_login_required
def taskLog(request):
        # 获取所有后台对象
        # page_len = request.GET.get('page_len', '')
        taskLog_list = models.BgTaskLog.objects.all().order_by('-bg_operation_time')
        log_list = []
        for i in taskLog_list:
            bg_id = i.bg_id
            taskManagement = models.BgTaskManagement.objects.get(bg_id=bg_id)
            bg_log_id = i.bg_log_id
            bg_module = taskManagement.bg_module
            bg_domain = taskManagement.bg_domain
            bg_operation_user =  i.bg_operation_user
            bg_operation = i.bg_operation
            bg_opr_result = i.bg_opr_result
            bg_operation_time = i.bg_operation_time
            log_dict = {"bg_log_id":bg_log_id,"bg_module": bg_module,"bg_domain":bg_domain,"bg_operation_user":bg_operation_user,"bg_operation":bg_operation,"bg_opr_result":bg_opr_result,"bg_operation_time":bg_operation_time}
            log_list.append(log_dict)
        p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(log_list, request)
        return render(request, "background/task_log.html", locals())

#后台日志搜索界面
@my_login_required
def taskLogSearch(request):
    log_list = []
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    bg_module = request.GET.get('bg_module')
    bg_domain = request.GET.get('bg_domain')
    bg_id_list = []
    # bg_operation = request.GET.get('bg_operation')
    #bg_opr_user = request.GET.get('bg_opr_user')
    if bg_domain and bg_module:
        tm = models.BgTaskManagement.objects.get(bg_domain=bg_domain,bg_module=bg_module)
        bg_id = tm.bg_id
        bg_id_list.append(bg_id)
    elif bg_domain:
        tm = models.BgTaskManagement.objects.filter(bg_domain=bg_domain)
        for i in tm:
            bg_id = i.bg_id
            bg_id_list.append(bg_id)
    elif bg_module:
        tm = models.BgTaskManagement.objects.filter(bg_module=bg_module)
        for i in tm:
            bg_id = i.bg_id
            bg_id_list.append(bg_id)
    for id in bg_id_list:
        if starttime and endtime:
            taskLog_list = BgTaskLog.objects.filter(bg_operation_time__gte=starttime, bg_operation_time__lte=endtime,bg_id=bg_id)
        else:
            taskLog_list = BgTaskLog.objects.filter(bg_id=id)
        for i in taskLog_list:
            bg_id = i.bg_id
            bg_log_id = i.bg_log_id
            taskManagement_i = models.BgTaskManagement.objects.get(bg_id=bg_id)
            bg_module = taskManagement_i.bg_module
            bg_domain = taskManagement_i.bg_domain
            bg_operation_user = i.bg_operation_user
            bg_operation = i.bg_operation
            bg_opr_result = i.bg_opr_result
            bg_operation_time = i.bg_operation_time
            log_dict = {"bg_log_id": bg_log_id, "bg_module": bg_module, "bg_domain": bg_domain,
                        "bg_operation_user": bg_operation_user, "bg_operation": bg_operation,
                         "bg_opr_result": bg_opr_result, "bg_operation_time": bg_operation_time}
            log_list.append(log_dict)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(log_list, request)
    return render(request, "background/task_log.html", locals())


#后台日志详情页面
@my_login_required
def taskLogDetail(request):
    bg_log_id = request.GET.get("bg_log_id")
    obj = get_object(BgTaskLog, bg_log_id=bg_log_id)
    log_dir = obj.bg_log_dir
    try:
        with open(log_dir, 'r+', encoding='utf-8') as f:
            log = f.read()
            log_info = log[0]
            print(log[0])
    except:
        log_info = "日志还未生成完毕"
    return render(request, 'background/task_log_detail.html', locals(),{'log':log_info,'log_dir':log_dir})
#文件下载
@my_login_required
def downloadTaskLog(request):
    log_dir = request.GET.get("log_dir")
    file=open(log_dir,'rb')
    downfilename = re.findall(r"log\\(.+?).log", log_dir)
    filename = str(downfilename[0])+".log"
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    #response['Content-Disposition']='attachment;filename="downfilename.log"'
    #response['Content-Disposition'] = 'attachment;filename=' + downfilename
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
    return response
