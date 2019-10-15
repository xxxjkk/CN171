# -*-coding:utf-8 -*-
import os
import re
import sys
import threading

from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from CN171_background import models
from CN171_background.api import pages,get_object
from django.shortcuts import render, redirect

from CN171_background.forms import BgForm
from CN171_background.models import BgTaskManagement, BgTaskLog
from CN171_tools import connecttool
from django.db.models import Q
from datetime import datetime

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
def taskExecuteOne(request):
    bg_id = request.GET.get('bg_id')
    bg_action = request.GET.get('bg_action')
    bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)

    if bg_action == 'start':
        cmd = bgTaskManagement.bg_task_start
    elif bg_action == 'stop':
        cmd = bgTaskManagement.bg_task_stop
    elif bg_action == 'restart':
        cmd = bgTaskManagement.bg_task_restart
    else:
        return redirect("taskManagement")

    connecttool.domainExecuteOne(cmd)
    return redirect("taskManagement")

# 批量启动按钮
def batchTaskStart(request):
    bg_ids = request.POST.getlist('ids', [])
    sshdStart = ssh_connect(conntarget)
    returnmsg = "true"
    msg = []
    a = 0
    threads = []
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if  bgTaskManagement.bg_status=="停止":
            bgTaskManagement.bg_status = "进行中"
            bgTaskManagement.save()
            cmd = bgTaskManagement.bg_task_start
            print(bgTaskManagement.bg_task_start)
            task = MyThread(ssh_exec_cmd, args=(sshdStart, cmd))
            threads.append(task)
        else:
            status_msg = False
            msg.append(status_msg)
      # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
    for i in threads:
        i.start()
        print(i.getName())
    for i in threads:
        i.join()
        stdin, stdout, stderr = i.get_result()
        err_list = stderr.readlines()
        if len(err_list) > 0:
            print('Start failed:' + err_list[0])
            failmsg = False
            msg.append(failmsg)
            bg_id = bg_ids[a]
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            taskManagement.bg_lastopr_user = request.session['user_name']
            taskManagement.bg_lastopr_time = datetime.now()
            taskManagement.bg_lastopr_result = "失败"
            taskManagement.bg_lastopr_type = "启动"
            taskManagement.bg_status = "停止"
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "启动" + taskManagement.bg_module + taskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "失败"
            taskManagement.save()
            # 写入日志文件
            file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                        "_" + "start" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result + err_list[0]
            path = config.get('TaskManagement', 'log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
            file.close()
            bg_log.save()
            a = a + 1
        else:
            print('Start success.')
            bg_id = bg_ids[a]
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            taskManagement.bg_lastopr_user = request.session['user_name']
            taskManagement.bg_lastopr_result = "成功"
            taskManagement.bg_lastopr_type = "启动"
            taskManagement.bg_status = "正常"
            taskManagement.bg_lastopr_time = datetime.now()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "启动" + taskManagement.bg_module + taskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "成功"
            taskManagement.save()
            # 写入日志文件
            file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                        "_" + "start" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            # str不支持时间格式直接相加
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result
            path = config.get(
                'TaskManagement',
                'log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
            file.close()
            bg_log.save()
            succedmsg = True
            msg.append(succedmsg)
            a = a + 1
        for item in stdout.readlines():
            print(item + i.getName())
    for j in msg:
        if not j:
            returnmsg = "false"
    ssh_close(sshdStart)
    return JsonResponse({'ret': returnmsg})
    #return redirect("taskManagement")


def batchTaskStop(request):
    bg_ids = request.POST.getlist('ids', [])
    sshdStop = ssh_connect(conntarget)
    returnmsg = "true"
    msg = []
    a = 0
    threads = []
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if  bgTaskManagement.bg_status == "正常"or bgTaskManagement.bg_status == "部分正常" or bgTaskManagement.bg_status == "异常" :
            cmd = bgTaskManagement.bg_task_stop
            old_status = bgTaskManagement.bg_status
            bgTaskManagement.bg_status = "进行中"
            print(bgTaskManagement.bg_task_stop)
            task = MyThread(ssh_exec_cmd, args=(sshdStop, cmd))
            threads.append(task)
            bgTaskManagement.save()
        else:
            status_msg = False
            msg.append(status_msg)
      # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
    for i in threads:
        i.start()
        print(i.getName())
    for i in threads:
        i.join()
        stdin, stdout, stderr = i.get_result()
        err_list = stderr.readlines()
        if len(err_list) > 0:
            print('Start failed:' + err_list[0])
            failmsg = False
            msg.append(failmsg)
            bg_id = bg_ids[a]
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            taskManagement.bg_lastopr_user = request.session['user_name']
            taskManagement.bg_lastopr_time = datetime.now()
            taskManagement.bg_lastopr_result = "失败"
            taskManagement.bg_lastopr_type = "停止"
            taskManagement.bg_status = old_status
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "停止" + taskManagement.bg_module + taskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "失败"
            taskManagement.save()
            # 写入日志文件
            file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                        "_" + "stop" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result + err_list[0]
            path = config.get(
                'TaskManagement', 'log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
            file.close()
            bg_log.save()
            a = a + 1
        else:
            print('Start success.')
            bg_id = bg_ids[a]
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            taskManagement.bg_lastopr_user = request.session['user_name']
            taskManagement.bg_lastopr_result = "成功"
            taskManagement.bg_lastopr_type = "停止"
            taskManagement.bg_status = "停止"
            taskManagement.bg_lastopr_time = datetime.now()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "停止" + taskManagement.bg_module + taskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "成功"
            taskManagement.save()
            # 写入日志文件
            file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                        "_" + "stop" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            # str不支持时间格式直接相加
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result
            path = config.get(
                'TaskManagement',
                'log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
            file.close()
            bg_log.save()
            succedmsg = True
            msg.append(succedmsg)
            a = a + 1
        for item in stdout.readlines():
            print(item + i.getName())
    for j in msg:
        if not j:
            returnmsg = "false"
    ssh_close(sshdStop)
    return JsonResponse({'ret': returnmsg})

# 批量重启
def batchTaskReboot(request):
    bg_ids = request.POST.getlist('ids', [])
    sshdStop = ssh_connect(conntarget)
    returnmsg = "true"
    msg = []
    a = 0
    threads = []
    for bg_id in bg_ids:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
        if bgTaskManagement.bg_status == "正常" or bgTaskManagement.bg_status == "部分正常" or bgTaskManagement.bg_status == "异常":
            cmd = bgTaskManagement.bg_task_restart
            old_status = bgTaskManagement.bg_status
            bgTaskManagement.bg_status = "进行中"
            print(bgTaskManagement.bg_task_restart)
            task = MyThread(ssh_exec_cmd, args=(sshdStop, cmd))
            threads.append(task)
            bgTaskManagement.save()
        else:
            status_msg = False
            msg.append(status_msg)

      # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
    for i in threads:
        i.start()
        print(i.getName())
    for i in threads:
        i.join()
        stdin, stdout, stderr = i.get_result()
        err_list = stderr.readlines()
        if len(err_list) > 0:
            print('Start failed:' + err_list[0])
            failmsg = False
            msg.append(failmsg)
            bg_id = bg_ids[a]
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            taskManagement.bg_lastopr_user = request.session['user_name']
            taskManagement.bg_lastopr_time = datetime.now()
            taskManagement.bg_lastopr_result = "失败"
            taskManagement.bg_lastopr_type = "重启"
            taskManagement.bg_status = old_status
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "重启" + taskManagement.bg_module + taskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "失败"
            taskManagement.save()
            # 写入日志文件
            file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                        "_" + "reboot" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result + err_list[0]
            path = config.get(
                'TaskManagement', 'log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
            file.close()
            bg_log.save()

            a = a + 1


        else:
            print('Start success.')
            bg_id = bg_ids[a]
            taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
            taskManagement.bg_lastopr_user = request.session['user_name']
            taskManagement.bg_lastopr_result = "成功"
            taskManagement.bg_lastopr_type = "重启"
            taskManagement.bg_status = "正常"
            taskManagement.bg_lastopr_time = datetime.now()
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "重启" + taskManagement.bg_module + taskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "成功"
            taskManagement.save()
            # 写入日志文件
            file_name = taskManagement.bg_module + "_" + taskManagement.bg_domain + \
                        "_" + "reboot" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            # str不支持时间格式直接相加
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result
            path = config.get(
                'TaskManagement',
                'log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
            file.close()
            bg_log.save()
            succedmsg = True
            msg.append(succedmsg)
            a = a + 1
        for item in stdout.readlines():
            print(item + i.getName())
    for j in msg:
        if not j:
            returnmsg = "false"
    ssh_close(sshdStop)
    return JsonResponse({'ret': returnmsg})


# 批量刷新页面
def reLoad(request):
    idlist = BgTaskManagement.objects.values_list('bg_id', flat=True)
    threads = []
    a=0
    returnmsg = "true"
    msg = []
    sshdReLoad = ssh_connect(conntarget)
    for id in idlist:
        bgTaskManagement = BgTaskManagement.objects.get(bg_id=id)
        cmd = bgTaskManagement.bg_task_query
        task = MyThread(ssh_exec_cmd, args=(sshdReLoad, cmd))
        threads.append(task)
        # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
        # print(task.getName())
    for i in threads:
        # 此时join的作用就凸显出来了，join所完成的工作就是线程同步，即主线程任务结束之后，进入阻塞状态，一直等待其他的子线程执行结束之后，主线程在终止
        i.start()
        print(i.getName())
    for i in threads:
        i.join()
        stdin, stdout, stderr = i.get_result()
        bg_id = idlist[a]
        err_list = stderr.readlines()
        if len(err_list) > 0:
            print('query failed:' + err_list[0])
            bg_log = BgTaskLog()
            bg_log.bg_id = bg_id
            bg_log.bg_operation = "刷新" + bgTaskManagement.bg_module + bgTaskManagement.bg_domain
            bg_log.bg_operation_time = datetime.now()
            bg_log.bg_operation_user = request.session['user_name']
            bg_log.bg_opr_result = "失败"
            # 写入日志文件
            file_name = bgTaskManagement.bg_module + "_" + bgTaskManagement.bg_domain + \
                        "_" + "reload" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
            bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                         bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result + err_list[0]
            path = config.get('TaskManagement','log_path') + file_name + '.log'
            bg_log.bg_log_dir = path
            file = open(path, 'a+')
            file.write('\n' + bg_log_msg)
            file.close()
            bg_log.save()
            failmsg = False
            msg.append(failmsg)
            a = a+1
        else:
            print('Start success.')
            for item in stdout.readlines():
                print(item)
                taskManagement = BgTaskManagement.objects.get(bg_id=bg_id)
                if  "查询结果:正常" in item:
                    taskManagement.bg_status = "正常"
                    a = a + 1
                elif "查询结果:部分正常" in item:
                    taskManagement.bg_status = "部分正常"
                    a = a + 1
                elif "查询结果:异常" in item:
                    taskManagement.bg_status = "异常"
                    a = a + 1
                elif  "查询结果:停止" in item:
                    taskManagement.bg_status = "停止"
                    a = a + 1
                elif "执行结果:成功" in item:
                    taskManagement.bg_lastopr_result = "成功"
                else:
                    print("执行出错")
                taskManagement.bg_lastopr_user = request.session['user_name']
                taskManagement.bg_lastopr_type = "查询"
                taskManagement.bg_lastopr_time = datetime.now()
                bg_log = BgTaskLog()
                bg_log.bg_id = bg_id
                bg_log.bg_operation = "刷新" + taskManagement.bg_module + taskManagement.bg_domain
                bg_log.bg_operation_time = datetime.now()
                bg_log.bg_operation_user = request.session['user_name']
                bg_log.bg_opr_result = "成功"
                taskManagement.save()
                # 写入日志文件
                file_name = bgTaskManagement.bg_module + "_" + bgTaskManagement.bg_domain + \
                            "_" + "reload" + "_" + datetime.now().strftime("%Y%m%d%H%I%S")
                # str不支持时间格式直接相加
                bg_log_msg = str(bg_log.bg_operation_time) + ":" + \
                             bg_log.bg_operation_user + bg_log.bg_operation + bg_log.bg_opr_result
                path = config.get(
                    'TaskManagement', 'log_path') + file_name + '.log'
                bg_log.bg_log_dir = path
                file = open(path, 'a+')
                file.write('\n' + bg_log_msg)  # msg也就是下面的Hello world!
                file.close()
                bg_log.save()
                succedmsg = True
                msg.append(succedmsg)
    for j in msg:
        if not j:
            returnmsg = "false"
    ssh_close(sshdReLoad)
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
def taskLogSearch(request):
    log_list = []
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    bg_module = request.GET.get('bg_module')
    bg_domain = request.GET.get('bg_domain')
    # bg_operation = request.GET.get('bg_operation')
    #bg_opr_user = request.GET.get('bg_opr_user')
    tm = models.BgTaskManagement.objects.get(bg_module=bg_module , bg_domain=bg_domain)
    print(tm.bg_module)
    bg_id = tm.bg_id
    taskLog_list = BgTaskLog.objects.filter(bg_operation_time__gte=starttime,bg_operation_time__lte=endtime,bg_id=bg_id)

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
def taskLogDetail(request):
    bg_log_id = request.GET.get("bg_log_id")
    obj = get_object(BgTaskLog, bg_log_id=bg_log_id)
    log_dir = obj.bg_log_dir
    with open(log_dir, 'r+') as f:
         log = f.read()
         print(log[0])
    return render(request, 'background/task_log_detail.html', locals(),{'log':log[0],'log_dir':log_dir})
#文件下载
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