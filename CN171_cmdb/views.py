import datetime
import time

from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from CN171_cmdb import models, forms, tasks
from django.shortcuts import render, redirect

from CN171_cmdb.exceloper import excel_export_host, excel_import_host, excel_import_app, excel_export_app
from CN171_cmdb.models import CmdbHost, CmdbApp, HostPwdOprLog, CmdbAppCluster, APP_STATUS
from CN171_cmdb.forms import DetailLogForm, HostPwdEditForm, NormalUserForm, CmdbHostForm, CmdbAppForm
from CN171_background.api import pages, get_object
from CN171_tools.common_api import export_download_txt, to_ints, write_txt, isNullStr, toInt
from CN171_tools.connecttool import *
from CN171_tools.sftputils import *
from CN171_account.views import my_login_required
import json

# Create your views here.

#def cmdbIndex(request):
#    return render(request, "cmdb/index.html", locals())
def text_save(filename, data):  # filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename, 'a')
    for i in range(len(data)):
        s = str(data[i]).replace('[', '').replace(']', '')  # 去除[],这两行按数据不同，可以选择
        s = s.replace("'", '').replace(',', '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符
        file.write(s)
    file.close()

#主机管理页面
def hostManagement(request):
    host_list = []
    keyword = request.GET.get("keyword", "")
    if keyword:
        host_list = models.CmdbHost.objects.filter(
            Q(cmdb_host_name__icontains=keyword) |
            Q(cmdb_host_type__icontains=keyword) |
            Q(cmdb_host_pod__icontains=keyword) |
            Q(cmdb_host_busip__icontains=keyword) |
            Q(cmdb_host_manip__icontains=keyword) |
            Q(cmdb_host_status__icontains=keyword)
        )
    else:
        host_list = models.CmdbHost.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_list, request)
    return render(request, "cmdb/host_management.html", locals())

#批量刷新主机状态信息
def batchRefreshHostStatusInfo(request):
    #ipQuerySet = CmdbHost.objects.values_list('cmdb_host_busip', flat=True)
    #ips = "";
    #ipQuerySetLen = len(ipQuerySet)
    #i = 0
    #for ip in ipQuerySet:
    #    ips = ips + ip
    #    if i < ipQuerySetLen - 1:
    #        ips = ips + "\r"
    #       i = i + 1
    host_busi_ip_all = request.POST.get('host_busi_ip_all')
    #ips=host_id_all.replace(",","\n")
    nowDay=datetime.datetime.now().strftime("%Y%m%d")
    #print(request.session.get('user_name'))
    user_name=request.session.get('user_name')
    #文件绝对路径
    file_name=write_txt(host_busi_ip_all, 'temp/cmdb/hostmgnt/status/'+nowDay+"/", user_name+'_refresh_host_status_busip')
    t, sftp = sftpconnect('CMIOT')
    ansible_host_hostmgnt_busiip_path, ansible_host_hostmgnt_return_filepath, ansible_host_hostmgnt_scrideploy_path\
        =get_hostmgnt_init_parameter('Ansible')
    flag = put(sftp,file_name,ansible_host_hostmgnt_busiip_path)
    sftpDisconnect(t)
    if flag:
        tasks.batchRefreshHostStatusTask.delay(ansible_host_hostmgnt_return_filepath,user_name,ansible_host_hostmgnt_scrideploy_path)
        returnmsg = "True"
    else:
        returnmsg = "False"
    return JsonResponse({'ret': returnmsg})

def hostDetail(request):
    hostId = request.GET.get("hostId")
    host = CmdbHost.objects.get(cmdb_host_id=hostId)
    return render(request, "cmdb/host_detail.html", locals())


def appManagement(request):
    app_list = []
    keyword = request.GET.get("keyword", "")
    if keyword:
        app_list = models.CmdbAppCluster.objects.filter(
            Q(app_name__icontains=keyword) |
            Q(app_status__icontains=keyword)
        )
    else:
        cluster_list = models.CmdbAppCluster.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(cluster_list, request)
    return render(request, "cmdb/app_management.html", locals())

#查询集群下的应用列表
def findAppsInCluster(request):
    clusterId = request.POST.get("clusterId")
    appCluster = CmdbAppCluster.objects.get(id=clusterId)
    appListInCluster=appCluster.cmdbApp_cmdbAppCluster.all()
    app_list = []
    for app in appListInCluster:
        app_dict = {}
        app_dict["app_id"] = app.app_id
        app_dict["app_name"] = app.app_name
        app_dict["cmdb_host_busip"] = app.cmdb_host.cmdb_host_busip
        app_dict["cmdb_host_manip"] = isNullStr(app.cmdb_host.cmdb_host_manip)
        app_dict["bg_module"] = app.cmdb_host.bg.bg_module
        app_dict["bg_domain"] = app.cmdb_host.bg.bg_domain
        appStatus=app.app_status
        a=int(appStatus)-1
        app_dict["app_status"] = APP_STATUS[a][1]
        app_dict["cmdb_host_system"] = isNullStr(app.cmdb_host.cmdb_host_system)
        app_dict["cmdb_host_cpu"] = isNullStr(app.cmdb_host.cmdb_host_cpu)
        app_dict["cmdb_host_RAM"] = isNullStr(app.cmdb_host.cmdb_host_RAM)
        app_dict["cmdb_host_local_disc"] = isNullStr(app.cmdb_host.cmdb_host_local_disc)
        app_dict["cmdb_host_outlay_disc"] = isNullStr(app.cmdb_host.cmdb_host_outlay_disc)
        app_dict["app_insert_time"] = app.app_insert_time.strftime("%Y-%m-%d %H:%M:%S")
        app_list.append(app_dict)
    ret = {'app_list': app_list,"appCount": len(appListInCluster)}
    v = json.dumps(ret)  # 转换为字典类型
    return HttpResponse(v)


#批量删除应用
def appDel(request):
    if request.method == 'POST':
        app_batch = request.GET.get('arg', '')
        app_id_all = str(request.POST.get('app_id_all', ''))

        if app_batch:
            for app_id in app_id_all.split(','):
                bg_item = get_object(CmdbHost, cmdb_host_id=app_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')

#添加应用
class CmdbAPPForm(object):
    pass

#GET 跳转到应用增加页面
#POST 应用添加功能
def appAdd(request):
    if request.method == 'GET':
        form = CmdbAppForm()
        return render(request, "cmdb/app_add.html", locals())
    else:
        ret = {'status': False, 'msg': '添加应用失败！', 'msg1': None}
        appForm = CmdbAppForm(request.POST)
        if appForm.is_valid():
            appForm.save()
            ret['status'] = True
            ret['msg'] = "添加应用成功！"
        else:
            ret['msg1'] = appForm.errors  # 这是一个对象
            print(appForm.errors)
        v = json.dumps(ret)  # 转换为字典类型
        return HttpResponse(v)

#批量删除应用集群
def appDel(request):
    if request.method == 'POST':
        app_batch = request.GET.get('arg', '')
        cluster_id_all = str(request.POST.get('cluster_id_all', ''))

        if app_batch:
            for cluster_id in cluster_id_all.split(','):
                bg_item = get_object(CmdbAppCluster, id=cluster_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')

#导出应用信息
def export_app_info(request):
    list_obj=[]
    cluster_id_all = to_ints(request.GET.get('cluster_id_all'))
    if cluster_id_all:
        list_cluster_obj=CmdbAppCluster.objects.filter(id__in=cluster_id_all)
    return excel_export_app(list_cluster_obj)

#导入应用信息
def import_app_info(request):
    ret = {'msg': None}
    file_obj = request.FILES.get('appInfoFile')
    if file_obj:
        ret['msg']= excel_import_app(file_obj)
    else:
        ret['msg'] = "请选择上传的文件！"
    v = json.dumps(ret)  # 转换为字典类型
    return HttpResponse(v)


#集群下的APP详情
def clusterAppDetail(request):
    clusterId=request.GET.get("clusterId")
    cluster_app_detail_list = models.CmdbApp.objects.filter( cluster_id=clusterId)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(cluster_app_detail_list,
                                                                                                request)
    return render(request, "cmdb/cluster_app_detail.html", locals())

#跳转到主机用户密码日志页面
def hostPwdOprLogPage(request):
    host_pwd_opr_log_list = models.HostPwdOprLog.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_pwd_opr_log_list, request)
    return render(request, "cmdb/host_pwd_opr_log.html", locals())

#主机用户密码操作日志列表
def hostPwdOprLog(request):
    host_pwd_opr_log_list = []
    keyword = request.GET.get("keyword", "")
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    host_pwd_opr_log_list = models.HostPwdOprLog.objects.all()
    if keyword:
        host_pwd_opr_log_list = host_pwd_opr_log_list.filter(
            Q(opr_user_name__icontains=keyword)
        )
    if starttime:
        host_pwd_opr_log_list=host_pwd_opr_log_list.filter(opr_time__gte =starttime)
    if endtime:
        host_pwd_opr_log_list= host_pwd_opr_log_list.filter(opr_time__lte =endtime)

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(host_pwd_opr_log_list, request)
    return render(request, "cmdb/host_pwd_opr_log.html", locals())

#主机用户密码详细日志
def hostPwdDetailLog(request):
        logId = request.GET.get("logId")
        flag = request.GET.get("flag")
        obj1 = HostPwdOprLog.objects.get(id= logId)
        if flag == '1':
            return  export_download_txt(obj1.detail_log)
        detailLogForm = DetailLogForm(instance=obj1)
        return render(request, "cmdb/host_pwd_detail_log.html", locals())


#跳转到主机用户密码修改页面
@my_login_required
def redEditHostPwdPage(request):
    form = HostPwdEditForm()
    return render(request, "cmdb/host_pwd_edit.html", locals())

#修改主机用户密码
def editHostPwd(request):
    form = HostPwdEditForm(request.POST, request.FILES)
    ret = {'status': False, 'msg': None,'form_status': True, 'msg1':None}
    opr_result = "失败"
    if form.is_valid():
        detail_log_info = ""
        file_obj = request.FILES.get('modified_host_list_file')
        modified_host_user =request.POST.get("modified_host_user")
        old_password = request.POST.get("old_password")
        username = request.session['user_name']
        file_path = os.path.join(BASE_DIR, "temp")
        path_not_exist_create(file_path)
        file_name_path=os.path.join(file_path,file_obj.name)
        try:
            #将文件从客户机浏览器写入到服务器
            f = open(file_name_path, 'wb')
            # chunks表示一块块的
            for line in file_obj.chunks():
                f.write(line)
            f.close()
            #将服务器文件sftp到Ansible主机
            client, sftp=sftpconnect("CMIOT")
            ansible_host_pwmgnt_ipfile_path=get_init_parameter2('Ansible')
            flag=put(sftp,file_name_path, ansible_host_pwmgnt_ipfile_path)
            sftpDisconnect(client)
            #执行命令
            #后期添加的这一句
            ansible_host_pwmgnt_ipfile=ansible_host_pwmgnt_ipfile_path+file_obj.name
            if(flag):
                detail_log_info, retStr = excute_edit_commond(ansible_host_pwmgnt_ipfile, modified_host_user, old_password)
                if retStr:
                    ret['status'] = True
                    ret['msg'] = "修改成功！"
                    opr_result="成功"
                else:
                    ret['msg'] = "修改失败，详细信息请查看日志！"
            else:
                ret['msg'] = "上传文件失败！"
        except Exception as e:
            print(e)
        # 保存操作记录
        hostPwdOprLog = HostPwdOprLog()
        hostPwdOprLog.opr_log_save(username, modified_host_user, opr_result, datetime.datetime.now(), detail_log_info)
    else:
        ret['msg1'] = form.errors  # 这是一个对象
        print(form.errors)
    v = json.dumps(ret)  # 转换为字典类型
    return HttpResponse(v)


#登录到相应的主机执行修改命令
def excute_edit_commond(ansible_host_pwmgnt_ipfile, modified_host_user, old_password):
    retStr = False
    #修改主机密码的命令
    cmd = "ansible -i %s all -u ansbmk -k -b -K -f 500 -m shell -a 'echo %s:%s|chpasswd'\r" \
          % (ansible_host_pwmgnt_ipfile, modified_host_user, old_password)
    #ansible普通用户密码
    ansible_host_pwmgnt_login_pwd,ansible_host_pwmgnt_root_pwd = get_init_parameter1("Ansible")
    cmd1 = "%s" % (ansible_host_pwmgnt_login_pwd+"\r")
    #ansibile root用户密码
    cmd2 = "%s" % (ansible_host_pwmgnt_root_pwd+"\r")
    trans, channel = build_shell_channel("Ansible")
    # 发送要执行的命令
    channel.send(cmd)
    while True:
        time.sleep(0.2)
        rst = channel.recv(1024)
        rst = rst.decode('utf-8')
        print(rst)
        # 通过命令执行提示符来判断命令是否执行完成
        if 'SSH password' in rst:
            channel.send(cmd1)  # SSH password  普通用户密码
            time.sleep(0.5)
            ret = channel.recv(1024)
            ret = ret.decode('utf-8')
            print(ret)
            if "SUDO password" in ret:
                channel.send(cmd2)  # ansibile主机 root用户密码
                time.sleep(0.5)
                detail_log = channel.recv(1024)
                detail_log = detail_log.decode('utf-8')
                print(detail_log)
                if "FAILED" not in detail_log and "SUCCESS" in detail_log:
                    retStr = True
                break
    close_shell_channel(trans, channel)
    return detail_log, retStr

#GET是跳转到用户主机页面，POST是添加主机
def hostAddPage(request):
    if request.method == "GET":
        form = CmdbHostForm()
        return render(request, 'cmdb/host_add.html', locals())
    else:
        ret = {'status': False, 'msg': '添加主机失败！','msg1':None}
        hostForm = CmdbHostForm(request.POST)
        if hostForm.is_valid():
            hostForm.save()
            ret['status'] = True
            ret['msg'] = "添加主机成功！"
        else:
            ret['msg1'] = hostForm.errors  # 这是一个对象
            print(hostForm.errors)
        v = json.dumps(ret)  # 转换为字典类型
        return HttpResponse(v)


#批量删除主机
def hostDel(request):
    if request.method == 'POST':
        host_batch = request.GET.get('arg', '')
        host_id_all = str(request.POST.get('host_id_all', ''))

        if host_batch:
            for cmdb_host_id in host_id_all.split(','):
                bg_item = get_object(CmdbHost, cmdb_host_id=cmdb_host_id)
                bg_item.delete()
    return HttpResponse(u'删除成功')

#导出主机信息
def export_host_info(request):
    list_obj=[]
    host_id_all = to_ints(request.GET.get('host_id_all'))
    if host_id_all:
        list_obj=CmdbHost.objects.filter(cmdb_host_id__in=host_id_all)
    return excel_export_host(list_obj)

#导入主机信息
def import_host_info(request):
    ret = {'msg': None}
    file_obj = request.FILES.get('hostInfoFile')
    if file_obj:
        ret['msg']= excel_import_host(file_obj)
    else:
        ret['msg'] = "请选择上传的文件！"
    v = json.dumps(ret)  # 转换为字典类型
    return HttpResponse(v)





