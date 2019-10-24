from django.http import HttpResponse
from django.shortcuts import render

from CN171_order.models import PbossOrderStatus,PbossOrderRecord,PbossOrderNode,PbossOrderRollback
from CN171_background.api import pages
from CN171_tools.connecttool import pbossOrderMake
from CN171_tools.mailutils import pbossOrderMakebyMail
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.

#PBOSS订单状态主函数
def pbossOrderStatus(request):
    order_list = PbossOrderStatus.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderStatus.html", locals())

#PBOSS订单状态查询后台函数
def pbossOrderStatusSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')

    order_list = PbossOrderStatus.objects.filter(order_starttime__gte=starttime,order_endtime__lte=endtime)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderStatus.html", locals())

#PBOSS订单状态生成后台函数
def pbossOrderStatusMake(request):
    starttime = request.POST.get('starttime')
    endtime  = request.POST.get('endtime')

    #若相关时间段已存在数据，是否仍然生成标识，由前台传入
    flag = request.POST.get('flag')

    if flag:
        return None
    else:
        order_list = PbossOrderStatus.objects.filter(order_starttime=starttime,order_endtime=endtime)
        if order_list:
            back_dic = {'existflag': "存在",'existdes': "相关时间段已经存在观察数据，是否仍然执行生成操作？"}
        else:
            pbrecord = PbossOrderRecord()
            pbrecord.record_type = "PBOSS订单-状态"
            pbrecord.record_mode = "手动生成"
            pbrecord.record_createtime = datetime.now()
            pbrecord.record_result = "执行中"
            pbrecord.record_filedir = "-"
            pbrecord.record_starttime = starttime
            pbrecord.record_endtime = endtime

            #ssh模式
            # execresult = pbossOrderMake("status")

            #邮件模式
            execresult = pbossOrderMakebyMail("status", starttime, endtime)


            if execresult == "成功":
                back_dic = {'executeflag': "成功"}
                pbrecord.record_result = "执行中"
            elif execresult == "失败":
                back_dic  = {'executeflag': "失败",'faildes': "执行异常"}
                pbrecord.record_result = "失败"

            pbrecord.save()
        import json
        return HttpResponse(json.dumps(back_dic))

#PBOSS订单节点主函数
def pbossOrderNode(request):
    order_list = PbossOrderNode.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderNode.html", locals())

#PBOSS订单节点查询后台函数
def pbossOrderNodeSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')

    order_list = PbossOrderNode.objects.filter(order_starttime__gte=starttime,order_endtime__lte=endtime)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderNode.html", locals())

#PBOSS订单节点生成后台函数
def pbossOrderNodeMake(request):
    starttime = request.POST.get('starttime')
    endtime  = request.POST.get('endtime')

    #若相关时间段已存在数据，是否仍然生成标识，由前台传入
    flag = request.POST.get('flag')

    if flag:
        return None
    else:
        order_list = PbossOrderNode.objects.filter(order_starttime=starttime,order_endtime=endtime)
        if order_list:
            back_dic = {'existflag': "存在",'existdes': "相关时间段已经存在观察数据，是否仍然执行生成操作？"}
        else:
            pbrecord = PbossOrderRecord()
            pbrecord.record_type = "PBOSS订单-节点"
            pbrecord.record_mode = "手动生成"
            pbrecord.record_createtime = datetime.now()
            pbrecord.record_result = "执行中"
            pbrecord.record_filedir = "-"
            pbrecord.record_starttime = starttime
            pbrecord.record_endtime = endtime

            #ssh模式
            # execresult = pbossOrderMake("node")

            #邮件模式
            execresult = pbossOrderMakebyMail("node", starttime, endtime)

            if execresult == "成功":
                back_dic = {'executeflag': "成功"}
                pbrecord.record_result = "执行中"
            elif execresult == "失败":
                back_dic  = {'executeflag': "失败",'faildes': "执行异常"}
                pbrecord.record_result = "失败"

            pbrecord.save()
        import json
        return HttpResponse(json.dumps(back_dic))

#PBOSS订单回退主函数
def pbossOrderRollback(request):
    order_list = PbossOrderRollback.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderRollback.html", locals())

#PBOSS订单回退查询后台函数
def pbossOrderRollbackSearch(request):
    starttime = request.GET.get('starttime')
    endtime  = request.GET.get('endtime')

    order_list = PbossOrderRollback.objects.filter(order_starttime__gte=starttime,order_endtime__lte=endtime)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
         order_list, request)
    return render(request, "order/pbossOrderRollback.html", locals())

#PBOSS订单回退生成后台函数
def pbossOrderRollbackMake(request):
    starttime = request.POST.get('starttime')
    endtime = request.POST.get('endtime')

    # 若相关时间段已存在数据，是否仍然生成标识，由前台传入
    flag = request.POST.get('flag')

    if flag:
        return None
    else:
        order_list = PbossOrderRollback.objects.filter(order_starttime=starttime, order_endtime=endtime)
        if order_list:
            back_dic = {'existflag': "存在", 'existdes': "相关时间段已经存在观察数据，是否仍然执行生成操作？"}
        else:
            pbrecord = PbossOrderRecord()
            pbrecord.record_type = "PBOSS订单-回退"
            pbrecord.record_mode = "手动生成"
            pbrecord.record_createtime = datetime.now()
            pbrecord.record_filedir = "-"
            pbrecord.record_starttime = starttime
            pbrecord.record_endtime = endtime

            #ssh模式
            # execresult = pbossOrderMake("rollback")

            #邮件模式
            execresult = pbossOrderMakebyMail("rollback", starttime, endtime)

            if execresult == "成功":
                back_dic = {'executeflag': "成功"}
                pbrecord.record_result = "执行中"
            elif execresult == "失败":
                back_dic = {'executeflag': "失败", 'faildes': "执行异常"}
                pbrecord.record_result = "失败"

            pbrecord.save()
        import json
        return HttpResponse(json.dumps(back_dic))

#PBOSS订单观察生成记录查询后台函数
def pbossMakeRecordQuery(request):
    record_list = PbossOrderRecord.objects.all()

    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(
        record_list, request)
    return render(request, "order/pbossMakeRecord.html", locals())

#PBOSS订单观察生成记录插入公共函数
def pbossMakeRecordInsert(request):
    return None


def test(request):
    return render(request, "test.html", locals())











