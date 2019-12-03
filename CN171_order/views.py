from django.http import HttpResponse,FileResponse
from django.shortcuts import render

from CN171_order.models import PbossOrderStatus,PbossOrderRecord,PbossOrderNode,PbossOrderRollback
from CN171_background.api import pages
from CN171_tools.mailutils import pbossOrderMakebyMail
from datetime import datetime
from CN171_account.views import my_login_required

# Create your views here.

#PBOSS订单状态主函数
@my_login_required
def pbossOrderStatus(request):
    order_list = PbossOrderStatus.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderStatus.html", locals())

#PBOSS订单状态查询后台函数
@my_login_required
def pbossOrderStatusSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')

    order_list = PbossOrderStatus.objects.filter(order_starttime__gte = starttime, order_endtime__lte = endtime)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderStatus.html", locals())

#PBOSS订单状态生成后台函数
@my_login_required
def pbossOrderStatusMake(request):
    starttime = request.POST.get('starttime')
    endtime  = request.POST.get('endtime')

    #调用PBOSS订单观察生成记录插入公共函数
    res = pbossMakeRecordInsert("状态", starttime, endtime)

    return res

#PBOSS订单节点主函数
@my_login_required
def pbossOrderNode(request):
    order_list = PbossOrderNode.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderNode.html", locals())

#PBOSS订单节点查询后台函数
@my_login_required
def pbossOrderNodeSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')

    order_list = PbossOrderNode.objects.filter(order_starttime__gte = starttime, order_endtime__lte = endtime)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderNode.html", locals())

#PBOSS订单节点生成后台函数
@my_login_required
def pbossOrderNodeMake(request):
    starttime = request.POST.get('starttime')
    endtime  = request.POST.get('endtime')

    # 调用PBOSS订单观察生成记录插入公共函数
    res = pbossMakeRecordInsert("节点", starttime, endtime)

    return res

#PBOSS订单回退主函数
@my_login_required
def pbossOrderRollback(request):
    order_list = PbossOrderRollback.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderRollback.html", locals())

#PBOSS订单回退查询后台函数
@my_login_required
def pbossOrderRollbackSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')

    order_list = PbossOrderRollback.objects.filter(order_starttime__gte = starttime, order_endtime__lte = endtime)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderRollback.html", locals())

#PBOSS订单回退生成后台函数
@my_login_required
def pbossOrderRollbackMake(request):
    starttime = request.POST.get('starttime')
    endtime = request.POST.get('endtime')

    # 调用PBOSS订单观察生成记录插入公共函数
    res = pbossMakeRecordInsert("回退", starttime, endtime)

    return res

#PBOSS订单观察生成记录主函数
@my_login_required
def pbossMakeRecord(request):
    record_list = PbossOrderRecord.objects.all()

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        record_list, request)
    return render(request, "order/pbossMakeRecord.html", locals())

#PBOSS订单观察生成记录查询后台函数
@my_login_required
def pbossMakeRecordSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')
    recordresult = request.GET.get('recordresult')

    #全部则将参数置空，不查询此参数
    if recordresult == "全部":
        recordresult = ""

    #判断参数是否为空，若均不为空，all([])返回True
    if all([starttime, endtime, recordresult]):
        record_list = PbossOrderRecord.objects.filter(record_starttime__gte = starttime, record_endtime__lte = endtime,
                                                  record_result = recordresult)
    elif all([starttime, recordresult]):
        record_list = PbossOrderRecord.objects.filter(record_starttime__gte=starttime, record_result=recordresult)
    elif all([endtime, recordresult]):
        record_list = PbossOrderRecord.objects.filter(record_endtime__lte = endtime, record_result=recordresult)
    elif all([starttime, endtime]):
        record_list = PbossOrderRecord.objects.filter(record_starttime__gte=starttime, record_endtime__lte=endtime)
    elif all([starttime]):
        record_list = PbossOrderRecord.objects.filter(record_starttime__gte=starttime)
    elif all([endtime]):
        record_list = PbossOrderRecord.objects.filter(record_endtime__lte=endtime)
    elif all([recordresult]):
        record_list = PbossOrderRecord.objects.filter(record_result=recordresult)
    else:
        record_list = PbossOrderRecord.objects.all()

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        record_list, request)
    return render(request, "order/pbossMakeRecord.html", locals())

#PBOSS订单观察生成记录插入公共函数
@my_login_required
def pbossMakeRecordInsert(type, starttime, endtime):
    record_type = "PBOSS订单-" + type
    order_record = PbossOrderRecord.objects.filter(record_type = record_type, record_result = "执行中",
                                                   record_starttime = starttime,record_endtime = endtime)
    if order_record:
        back_dic = {'existflag': "存在",'existdes': "相关起始时间段已经存在执行中的任务，请等待执行完成后再进行新的生成操作，"
                                                  "详情请见生成记录！"}
    else:
        pbrecord = PbossOrderRecord()
        pbrecord.record_type = record_type
        pbrecord.record_mode = "手动生成"
        pbrecord.record_createtime = datetime.now()
        pbrecord.record_result = "执行中"
        pbrecord.record_filedir = "-"
        pbrecord.record_starttime = starttime
        pbrecord.record_endtime = endtime

        #ssh模式
        # execresult = pbossOrderMake("status")

        #邮件模式
        execresult = pbossOrderMakebyMail(type, starttime, endtime)

        if execresult == "成功":
            back_dic = {'executeflag': "成功"}
            pbrecord.record_result = "执行中"
        elif execresult == "失败":
            back_dic  = {'executeflag': "失败",'faildes': "执行异常"}
            pbrecord.record_result = "失败"

        pbrecord.save()
    import json
    return HttpResponse(json.dumps(back_dic))


#文件下载
@my_login_required
def downloadRecordFile(request):
    log_dir = request.GET.get("log_dir")
    file=open(log_dir,'rb')

    #适配Linux环境，截取日志文件名
    if '/' in log_dir:
        downfilename = log_dir.split('/')[-1]
    #适配Windows环境，截取日志文件名
    elif '\\' in log_dir:
        downfilename = log_dir.split('\\')[-1]
    else:
        response = "Log file not exits!"
        return response

    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(downfilename)
    return response










