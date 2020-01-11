from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from CN171_aiops.models import PbossWarningAnalysis, PbossWarningNum, PbossWarningKPI
import json
import time

#告警采集间隔（以分钟为单位）
INTERVAL = 30

#容量预测主函数
from CN171_aiops import models
from CN171_aiops.action import taskAction, checkGenerate
from CN171_aiops.models import AiopsDetectLog, TableSpaceDict
from CN171_background.api import pages


def capacity(request):
    aiopsDetectLog = models.AiopsDetectLog.objects.all()
    aiopsDetectLog_list = []
    for i in aiopsDetectLog:
        tablespacedict = i.ai_tablespacedict
        tablespace_name = tablespacedict.tablespace_name
        DB_Name = tablespacedict.DB_Name
        create_time = i.create_time
        capacity_total = i.capacity_total
        alarm_threshold = i.alarm_threshold
        start_time = i.start_time
        end_time = i.end_time
        result = i.result
        status = i.status
        id = i.id
        aiopslog_info = {"id": id, "tablespace_name": tablespace_name, "DB_Name": DB_Name, "create_time": create_time,
                     "capacity_total": capacity_total, "alarm_threshold": alarm_threshold,
                     "start_time": start_time, "end_time": end_time , "result": result,"status": status}
        aiopsDetectLog_list.append(aiopslog_info)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(aiopsDetectLog_list, request)
    return render(request, "aiops/capacity.html", locals())


# 容量预测生成
def capacityDetect(request):
    tablespace_name = request.POST.get('tablespace')
    DB_Name = request.POST.get('dbname')
    start_time = request.POST.get('starttime')
    end_time = request.POST.get('endtime')
    # capacity_total = request.POST.get('capacity_total')
    alarm_threshold = request.POST.get('alarm_threshold')
    create_time = datetime.now()
    aiopsDetectLog = AiopsDetectLog()
    aiopsDetectLog.alarm_threshold = alarm_threshold
    # aiopsDetectLog.capacity_total = capacity_total
    aiopsDetectLog.start_time = start_time
    aiopsDetectLog.end_time = end_time
    aiopsDetectLog.create_time = create_time
    aiopsDetectLog.status = "待执行"
    tableSpaceDict = models.TableSpaceDict.objects.filter(Q(tablespace_name=tablespace_name)&Q(DB_Name=DB_Name))
    print(tableSpaceDict[0].DB_Name)
    #保存数据库表空间外键字段
    if tableSpaceDict:
        aiopsDetectLog.ai_tablespacedict = tableSpaceDict[0]
        aiopsDetectLog.save()
    id = aiopsDetectLog.id
    # aiopsDetectLog = AiopsDetectLog(ai_tablespacedict = tableSpaceDict)
    taskAction(id,DB_Name,tablespace_name,start_time,end_time,alarm_threshold,create_time)
    checkGenerate()
    return JsonResponse({'ret': "True"})

# 容量预测结果图表生成
def resultEcharts(request,id):
    aiopsDetectLog = models.AiopsDetectLog.objects.get(id=id)
    createtime = aiopsDetectLog.create_time
    createtime = createtime.strftime("%Y-%m-%d %H:%M:%S.000000")
    DB_Name = aiopsDetectLog.ai_tablespacedict.DB_Name
    tablespace_name = aiopsDetectLog.ai_tablespacedict.tablespace_name
    tableSpaceDict = models.TableSpaceDict.objects.filter(Q(tablespace_name=tablespace_name) & Q(DB_Name=DB_Name))
    DetectResult_list = models.DetectResult.objects.filter(create_time__gte=createtime,create_time__lte=createtime)
    print(DetectResult_list[0].origin)
    return render(request, "aiops/resultEcharts.html", locals())

# 智能告警分析（PBOSS）主函数
#容量预测结果搜索
def resultSearch(request):
    tablespace_name = request.GET.get('tablespace_name')
    tableSpaceDict = models.TableSpaceDict.objects.filter(tablespace_name=tablespace_name)
    aiopsDetectLog_list = []
    for i in tableSpaceDict:
        aiopsDetectLog = models.AiopsDetectLog.objects.filter(ai_tablespacedict=i)
        tablespace_name = i.tablespace_name
        DB_Name = i.DB_Name
        for j in aiopsDetectLog:
            create_time = j.create_time
            capacity_total = j.capacity_total
            alarm_threshold = j.alarm_threshold
            start_time = j.start_time
            end_time = j.end_time
            result = j.result
            status = j.status
            id = j.id
            aiopslog_info = {"id": id, "tablespace_name": tablespace_name, "DB_Name": DB_Name, "create_time": create_time,
                             "capacity_total": capacity_total, "alarm_threshold": alarm_threshold,
                             "start_time": start_time, "end_time": end_time, "result": result, "status": status}
            aiopsDetectLog_list.append(aiopslog_info)
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(aiopsDetectLog_list,request)
    return render(request, "aiops/capacity.html", locals())



#智能告警分析（PBOSS）主函数
def warningPboss(request):
    # warning_analysis = PbossWarningAnalysis.objects.filter().order_by("warning_id")
    # p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(warning_analysis, request)
    # warning_num = PbossWarningNum.objects.filter().last()
    warning_kpi_all = PbossWarningKPI.objects.all()
    length = warning_kpi_all.count()
    if length < 16:
        warning_kpi = warning_kpi_all
    else:
        warning_kpi = warning_kpi_all[length - 16:length]

    return render(request, "aiops/warningpboss.html", locals())


def warningPbossUpdateNum(request):
    if request.method == "POST":
        warning_num = PbossWarningNum.objects.filter().last()
        num = {}
        if warning_num:
            solving_num = [warning_num.warning_backlog_solving,
                           warning_num.warning_orderfailed_solving,
                           warning_num.warning_appfailed_solving,
                           warning_num.warning_disk_solving,
                           warning_num.warning_whole_solving,
                           warning_num.warning_other_solving]
            pre_solved_num = [warning_num.warning_backlog_pre_solved,
                              warning_num.warning_orderfailed_pre_solved,
                              warning_num.warning_appfailed_pre_solved,
                              warning_num.warning_disk_pre_solved,
                              warning_num.warning_whole_pre_solved,
                              warning_num.warning_other_pre_solved]
        else:
            solving_num = [0, 0, 0, 0, 0, 0]
            pre_solved_num = [0, 0, 0, 0, 0, 0]
        num["solving_num"] = solving_num
        num["pre_solved_num"] = pre_solved_num
        return HttpResponse(json.dumps(num))


def warningPbossUpdateKpi(request):
    if request.method == "POST":
        warning_kpi = PbossWarningKPI.objects.filter().last()
        percent = {"warning_runtime": str(warning_kpi.warning_runtime),
                   "interface_success1": str(warning_kpi.warning_interface_success1),
                   "interface_success2": str(warning_kpi.warning_interface_success2),
                   "warning_service_success": str(warning_kpi.warning_service_success),
                   "warning_query_success": str(warning_kpi.warning_query_success)}
        return HttpResponse(json.dumps(percent))


def warningPbossUpdateAnalysis(request):
    if request.method == "POST":
        warning_analysis1 = PbossWarningAnalysis.objects.filter(warning_status="处理中")
        warning_analysis2 = PbossWarningAnalysis.objects.filter(warning_status="预解决")
        warnings = {}
        id = 0
        for warning in warning_analysis2:
            pre_solvedtime = str(warning.warning_pre_solvedtime)
            starttime = str(warning.warning_starttime)
            timeStamp_start = int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
            timeStamp_end = time.localtime(timeStamp_start + INTERVAL * 60)
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', timeStamp_end)
            if pre_solvedtime >= starttime and pre_solvedtime < endtime:
                id += 1
                warnings[id] = [id,
                                str(warning.warning_message),
                                str(warning.warning_number),
                                str(warning.warning_arisingtime),
                                str(warning.warning_status),
                                str(warning.warning_reason1)]
        for warning in warning_analysis1:
            id += 1
            warnings[id] = [id,
                            str(warning.warning_message),
                            str(warning.warning_number),
                            str(warning.warning_arisingtime),
                            str(warning.warning_status),
                            str(warning.warning_reason1)]
        return HttpResponse(json.dumps(warnings, ensure_ascii=False))


def warningDetail(request):
    warningMessage = request.GET.get("warningMessage")
    warning_analysis_detail = PbossWarningAnalysis.objects.get(warning_message=warningMessage)
    return render(request, "aiops/warningDetail.html", locals())