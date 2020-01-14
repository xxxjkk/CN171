#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/13 10:57
# @Author: zhaocy
# @Time  : 2020/1/3
# @Author: liuyx
# @File  : excelutil.py
# @Software: CN171

import os,shutil
import pandas
import time
import re

from django.db.models import Q

from CN171_aiops import models
from CN171_aiops.models import DetectResult
from CN171_aiops.models import PbossWarningAnalysis, PbossWarningNum

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#告警采集间隔（以分钟为单位）
INTERVAL = 30

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'), encoding='utf-8')

#文件路径和备份路径
localfiledir = config.get('AIopsCapacity', 'AIopsCapacity_result_path')
local_filedir = config.get('WARNING', 'pboss_warning_local_filedir')
local_filebakdir = config.get('WARNING', 'pboss_warning_local_filedirbak')

def resultExcelRead(filepath,filename):
    # 文件名分拆
    fndisass = fileNameDisass(filename)
    createtime = fndisass.get('createtime')
    DB_Name = fndisass.get('DB_Name')
    tablespace_name = fndisass.get('tablespace_name')

    # 开始解析上传的excel表格
    df = pandas.DataFrame(pandas.read_excel(filepath))
    # 获取表头
    df_head = df.columns.values.tolist()
    tableSpaceDict = models.TableSpaceDict.objects.filter(Q(tablespace_name=tablespace_name) & Q(DB_Name=DB_Name))
    # 文件数据入库
    for i in range(df.shape[0]):
        detectResult = DetectResult()
        detectResult.create_time = createtime
        detectResult.ai_tablespacedict = tableSpaceDict[0]
        for j in range(len(df_head)):
            if df_head[j] == "time":
                detectResult.detect_time = df.iloc[i, j]
            elif df_head[j] == "origin":
                detectResult.origin = df.iloc[i, j]
            elif df_head[j] == "predict":
                detectResult.predict = df.iloc[i, j]
        detectResult.save()
    return None


#文件名分拆函数
def fileNameDisass(file):
    # 迁移前文件路径、迁移后文件路径
    dstfile = file

    # 截取文件名中的开始时间、结束时间
    file_name = file.split('.')[0]
    createtimestr = None
    if '_' in file_name:
        createtimestr = file_name.split('_')[-1]
        DB_Name = file_name.split('_')[-3]
        tablespace_name = file_name.split('_')[-2]
    createtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(createtimestr, '%Y%m%d%H%M%S'))

    #将文件名分拆结果组成list
    fndisass = {'dstfile': dstfile, 'createtime': createtime, 'DB_Name': DB_Name, 'tablespace_name': tablespace_name}

    return fndisass


# #记录入库函数
# def recordSave(starttime, endtime, file, dstfile, type):
#     # 判断是否有执行中的任务，若有则以任务的创建时间为准，并更新任务状态、文件路径
#     record = PbossOrderRecord.objects.filter(record_starttime=starttime, record_endtime=endtime,
#                                              record_result="执行中", record_type=type).first()
#     if record:
#         record.record_result = "成功"
#         record.record_filedir = localfilebakdir + file
#         record.save()
#         return record
#     else:
#         createtime = datetime.now()
#
#         # 新增新的记录
#         newrecord = PbossOrderRecord()
#         newrecord.record_type = type
#         newrecord.record_starttime = starttime
#         newrecord.record_endtime = endtime
#         newrecord.record_createtime = createtime
#         newrecord.record_mode = "自动生成"
#         newrecord.record_result = "成功"
#         newrecord.record_filedir = dstfile
#         newrecord.save()
#         return newrecord

# excel文件读取主函数
def excelRead():
    # 获取文件夹下的所有文件
    files = os.listdir(local_filedir)

    for file in files:
        # 判断是否为以PBOSS开头、.xlsx结尾的Excel文件
        file_name = file.split('.')[0]
        file_ext = file.split('.')[1]
        if ('xlsx' == file_ext) and (file.startswith('PBOSS')):
            file_type = file_name.split('_')[1]
            file_time = str(file_name.split('_')[2])
            if file_type == 'WARNING' and isVaildTime(file_time):
                warningExcelAnalysis(file, file_time)
            else:
                print("未知类型文件《" + file + "》，不进行处理")
        time.sleep(1)

# 告警分析excel文件读函数
def warningExcelAnalysis(file, file_time):
    srcfile = local_filedir + file
    dstfile = local_filebakdir + file

    # 本轮次开始时间
    starttime = time.strftime('%Y-%m-%d %H:%M:00', time.strptime(file_time, '%Y%m%d%H%M'))
    timeStamp_start = int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
    # 本轮次结束时间
    timeStamp_end = time.localtime(timeStamp_start + INTERVAL * 60)
    endtime = time.strftime('%Y-%m-%d %H:%M:%S', timeStamp_end)

    updatingtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    print("1.插入新增告警")
    # 开始解析上传的excel表格
    df = pandas.DataFrame(pandas.read_excel(srcfile))
    # 文件数据入库（PbossWarningAnalysis）
    for i in range(df.shape[0]):
        pbswarning = PbossWarningAnalysis()
        # 告警内容
        pbswarning.warning_message = df.iloc[i, 0]
        # 告警类别
        pbswarning.warning_type = warningType(df.iloc[i, 0])
        # 告警数量
        pbswarning.warning_number = df.iloc[i, 1]
        # 告警发生时间
        arisingtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(df.iloc[i, 2], '%Y.%m.%d %H:%M:%S'))
        pbswarning.warning_arisingtime = arisingtime
        # 告警更新时间
        pbswarning.warning_updatingtime = updatingtime
        # 告警预计解决时间
        timeStamp_arising = int(time.mktime(time.strptime(df.iloc[i, 2], '%Y.%m.%d %H:%M:%S')))
        timeStamp_pre_solvedtime = time.localtime(timeStamp_arising + df.iloc[i, 7] * 60)
        pbswarning.warning_pre_solvedtime = time.strftime('%Y-%m-%d %H:%M:%S', timeStamp_pre_solvedtime)
        # 统计开始时间
        pbswarning.warning_starttime = starttime
        # 告警状态
        pbswarning.warning_status = df.iloc[i, 3]
        # 告警原因
        pbswarning.warning_reason1 = df.iloc[i, 4]
        pbswarning.warning_reason2 = df.iloc[i, 5]
        pbswarning.warning_reason3 = df.iloc[i, 6]
        pbswarning.save()

    print("2.更新告警状态")
    # 判断是否有预解决的告警，更新状态为预解决
    recordUpdate(starttime, endtime, updatingtime)

    print("3.统计告警数量")
    # 统计各类告警数量，入库（PbossWarningNum）
    warningNum(updatingtime)

    # 文件迁移
    shutil.move(srcfile, dstfile)

    return None


# 判断是否是有效的时间
def isVaildTime(file_time):
    try:
        starttime = time.strptime(file_time, "%Y%m%d%H%M")
        if starttime.tm_min % INTERVAL == 0:
            return True
        else:
            return False
    except:
        return False


# 判断告警类别
def warningType(message):
    # 环节积压
    parttern1_1 = re.compile(r'订单积压')
    parttern1_2 = re.compile(r'环节积压')
    # 环节异常
    parttern2_1 = re.compile(r'环节异常')
    parttern2_2 = re.compile(r'，处理异常：')
    # 集群/应用异常
    parttern3_1 = re.compile(r'TOMCAT(.*?)异常')
    parttern3_2 = re.compile(r'集群节点异常')
    # 磁盘/表空间告警
    parttern4 = re.compile(r'disk warning')
    # 全网监控预警
    parttern5 = re.compile(r'成功率(.*?)[-]')
    if re.search(parttern1_1, message) or re.search(parttern1_2, message):
        warning_type = "环节积压"
        return warning_type
    elif re.search(parttern2_1, message) or re.search(parttern2_2, message):
        warning_type = "环节异常"
        return warning_type
    elif re.search(parttern3_1, message) or re.search(parttern3_2, message):
        warning_type = "集群/应用异常"
        return warning_type
    elif re.search(parttern4, message):
        warning_type = "磁盘/表空间告警"
        return warning_type
    elif re.search(parttern5, message):
        warning_type = "全网监控预警"
        return warning_type
    else:
        warning_type = "其它"
        return warning_type


# 判断是否有预解决的告警，更新状态为预解决
def recordUpdate(starttime, endtime, updatingtime):
    records = PbossWarningAnalysis.objects.filter(warning_status="处理中")
    for record in records:
        pre_solvedtime = str(record.warning_pre_solvedtime)
        if pre_solvedtime >= starttime and pre_solvedtime < endtime:
            record.warning_updatingtime = updatingtime
            record.warning_status = "预解决"
            record.save()
    return None


# 统计各类告警数量，入库（PbossWarningNum）
def warningNum(updatetime):
    # 已解决数量
    backlog_solving_num = 0
    orderfailed_solving_num = 0
    appfailed_solving_num = 0
    disk_solving_num = 0
    whole_solving_num = 0
    other_solving_num = 0
    # 预解决数量
    backlog_pre_solved_num = 0
    orderfailed_pre_solved_num = 0
    appfailed_pre_solved_num = 0
    disk_pre_solved_num = 0
    whole_pre_solved_num = 0
    other_pre_solved_num = 0

    records_solving = PbossWarningAnalysis.objects.filter(warning_status="处理中")
    for record in records_solving:
        if record.warning_type == "环节积压":
            backlog_solving_num += 1
        elif record.warning_type == "环节异常":
            orderfailed_solving_num += 1
        elif record.warning_type == "集群/应用异常":
            appfailed_solving_num += 1
        elif record.warning_type == "磁盘/表空间告警":
            disk_solving_num += 1
        elif record.warning_type == "全网监控预警":
            whole_solving_num += 1
        else:
            other_solving_num += 1

    records_pre_solved = PbossWarningAnalysis.objects.filter(warning_status="预解决", warning_updatingtime=updatetime)
    for record in records_pre_solved:
        if record.warning_type == "环节积压":
            backlog_pre_solved_num += 1
        elif record.warning_type == "环节异常":
            orderfailed_pre_solved_num += 1
        elif record.warning_type == "集群/应用异常":
            appfailed_pre_solved_num += 1
        elif record.warning_type == "磁盘/表空间告警":
            disk_pre_solved_num += 1
        elif record.warning_type == "全网监控预警":
            whole_pre_solved_num += 1
        else:
            other_pre_solved_num += 1

    pbswarning_num = PbossWarningNum()
    pbswarning_num.warning_runtime = updatetime
    pbswarning_num.warning_backlog_solving = backlog_solving_num
    pbswarning_num.warning_orderfailed_solving = orderfailed_solving_num
    pbswarning_num.warning_appfailed_solving = appfailed_solving_num
    pbswarning_num.warning_disk_solving = disk_solving_num
    pbswarning_num.warning_whole_solving = whole_solving_num
    pbswarning_num.warning_other_solving = other_solving_num
    pbswarning_num.warning_backlog_pre_solved = backlog_pre_solved_num
    pbswarning_num.warning_orderfailed_pre_solved = orderfailed_pre_solved_num
    pbswarning_num.warning_appfailed_pre_solved = appfailed_pre_solved_num
    pbswarning_num.warning_disk_pre_solved = disk_pre_solved_num
    pbswarning_num.warning_whole_pre_solved = whole_pre_solved_num
    pbswarning_num.warning_other_pre_solved = other_pre_solved_num
    pbswarning_num.save()

    return None
