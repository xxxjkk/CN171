from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.



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
    return render(request, "aiops/warningpboss.html", locals())