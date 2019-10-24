#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/8 16:26
# @Author: zhulong
# @File  : excelutils.py
# @Software: CN171

import os,shutil
import pandas
import time
from django.shortcuts import render
from CN171_order.models import PbossOrderStatus,PbossOrderRecord,PbossOrderNode,PbossOrderRollback
from datetime import datetime

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'))

#文件路径和备份路径
localfiledir = config.get('PBOSS', 'pboss_order_local_filedir')
localfilebakdir = config.get('PBOSS', 'pboss_order_local_filedirbak')

#excel文件读取主函数
def excelread(request):
    #获取文件夹下的所有文件
    files = os.listdir(localfiledir)

    for file in files:
        #判断是否为以PBOSS开头、.xlsx结尾的Excel文件
        file_ext = file.split('.')[1]
        if ('xlsx' == file_ext) and (file.startswith('PBOSS')):
            file_name = file.split('.')[0]
            if '_' in file_name:
                file_type = file_name.split('_')[-4]
            elif ' ' in file_name:
                file_type = file_name.split(' ')[-4]
            if file_type == "状态":
                statusExcelRead(file)
            elif file_type == "节点":
                nodeExcelRead(file)
            elif file_type == "回退":
                rollbackExcelRead(file)
            else:
                print("未知类型文件《" + file + "》，不进行处理")
        else:
            print("未知类型文件《" + file + "》，不进行处理")

    return render(request, "test.html")

#状态类型excel文件读函数
def statusExcelRead(file):
    #迁移前文件路径、迁移后文件路径
    srcfile = localfiledir + file
    dstfile = localfilebakdir + file

    # 开始解析上传的excel表格
    df = pandas.DataFrame(pandas.read_excel(srcfile))

    # 截取文件名中的开始时间、结束时间
    file_name = file.split('.')[0]
    if '_' in file_name:
        starttimestr = file_name.split('_')[-3]
        endtimestr = file_name.split('_')[-1]
    elif ' ' in file_name:
        starttimestr = file_name.split(' ')[-3]
        endtimestr = file_name.split(' ')[-1]
    starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(starttimestr, '%Y%m%d%H%M%S'))
    endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(endtimestr, '%Y%m%d%H%M%S'))

    # 判断是否有执行中的任务，若有则以任务的创建时间为准，并更新任务状态、文件路径
    record = recordSave(starttime, endtime, file, dstfile, "PBOSS订单-状态")

    #文件迁移
    shutil.move(srcfile,dstfile)

    # 获取表头
    df_head = df.columns.values.tolist()

    #找到表中名称对应列
    for i in range(len(df_head)):
        if df_head[i] == "CODENAME":
            namecol = i

    #文件数据入库
    for i in range(len(df_head)):
        if (df_head[i] != "CODENAME") and (df_head[i] != "CODEFLAG"):
            pbstatus = PbossOrderStatus()
            pbstatus.order_area = df_head[i]
            pbstatus.order_starttime = starttime
            pbstatus.order_endtime = endtime
            pbstatus.order_createtime = record.record_createtime
            for j in range(df.shape[0]):
                if df.iloc[j, namecol] == "结束":
                    pbstatus.order_finish = df.iloc[j, i]
                elif df.iloc[j, namecol] == "计费反馈同步失败":
                    pbstatus.order_cbbsfailed = df.iloc[j, i]
                elif df.iloc[j, namecol] == "流程启动异常":
                    pbstatus.order_startfailed = df.iloc[j, i]
                elif df.iloc[j, namecol] == "同步计费中":
                    pbstatus.order_cbbssyncing = df.iloc[j, i]
                elif df.iloc[j, namecol] == "发起同步失败":
                    pbstatus.order_syncfailed = df.iloc[j, i]
                elif df.iloc[j, namecol] == "已发送计费同步请求":
                    pbstatus.order_cbbssynced = df.iloc[j, i]
                elif df.iloc[j, namecol] == "已竣工":
                    pbstatus.order_completed = df.iloc[j, i]
                elif df.iloc[j, namecol] == "待施工处理":
                    pbstatus.order_pending = df.iloc[j, i]
                elif df.iloc[j, namecol] == "施工处理中":
                    pbstatus.order_processing = df.iloc[j, i]
                elif df.iloc[j, namecol] == "待同步计费":
                    pbstatus.order_cbbssyncpending = df.iloc[j, i]
                print(pbstatus.order_area, df.iloc[j,i])
            pbstatus.save()
    return None

#节点类型excel文件读函数
def nodeExcelRead(file):
    # 迁移前文件路径、迁移后文件路径
    srcfile = localfiledir + file
    dstfile = localfilebakdir + file

    # 开始解析上传的excel表格
    df = pandas.DataFrame(pandas.read_excel(srcfile))

    # 截取文件名中的开始时间、结束时间
    file_name = file.split('.')[0]
    starttimestr = file_name.split('_')[-3]
    endtimestr = file_name.split('_')[-1]
    starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(starttimestr, '%Y%m%d%H%M%S'))
    endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(endtimestr, '%Y%m%d%H%M%S'))

    # 判断是否有执行中的任务，若有则以任务的创建时间为准，并更新任务状态、文件路径
    record = recordSave(starttime, endtime, file, dstfile, "PBOSS订单-节点")

    # 文件迁移
    shutil.move(srcfile, dstfile)

    # 获取表头
    df_head = df.columns.values.tolist()

    #找到表中名称对应列
    for i in range(len(df_head)):
        if df_head[i] == "NODENAME":
            namecol = i

    # 文件数据入库
    for i in range(len(df_head)):
        if (df_head[i] != "NODENAME") and (df_head[i] != "SYSDATE") and (df_head[i] != "NODEID"):
            pbnode = PbossOrderNode()
            pbnode.order_area = df_head[i]
            pbnode.order_starttime = starttime
            pbnode.order_endtime = endtime
            pbnode.order_createtime = record.record_createtime
            for j in range(df.shape[0]):
                if df.iloc[j, namecol] == "HLR节点":
                    pbnode.order_HLR = df.iloc[j, i]
                elif df.iloc[j, namecol] == "运管平台":
                    pbnode.order_IOMP = df.iloc[j, i]
                elif df.iloc[j, namecol] == "业务网关":
                    pbnode.order_SMSGateway = df.iloc[j, i]
                elif df.iloc[j, namecol] == "一级BOSS枢纽反馈":
                    pbnode.order_BOSSHub = df.iloc[j, i]
                elif df.iloc[j, namecol] == "内容计费":
                    pbnode.order_CBBS = df.iloc[j, i]
                elif df.iloc[j, namecol] == "竣工":
                    pbnode.order_Complete = df.iloc[j, i]
                elif df.iloc[j, namecol] == "物联网行车卫士业务平台":
                    pbnode.order_XCWS = df.iloc[j, i]
                elif df.iloc[j, namecol] == "PCRF平台":
                    pbnode.order_PCRF = df.iloc[j, i]
                elif df.iloc[j, namecol] == "车联网SCP":
                    pbnode.order_SCP = df.iloc[j, i]
                elif df.iloc[j, namecol] == "和对讲业务平台":
                    pbnode.order_POC = df.iloc[j, i]
                elif df.iloc[j, namecol] == "物漫平台":
                    pbnode.order_TRSS = df.iloc[j, i]
                elif df.iloc[j, namecol] == "号码回收节点":
                    pbnode.order_NumRecycle = df.iloc[j, i]
                print(pbnode.order_area, df.iloc[j, i])
            pbnode.save()
    return None

#回退类型excel文件读函数
def rollbackExcelRead(file):
    # 迁移前文件路径、迁移后文件路径
    srcfile = localfiledir + file
    dstfile = localfilebakdir + file

    # 开始解析上传的excel表格
    df = pandas.DataFrame(pandas.read_excel(srcfile))

    # 截取文件名中的开始时间、结束时间
    file_name = file.split('.')[0]
    starttimestr = file_name.split('_')[-3]
    endtimestr = file_name.split('_')[-1]
    starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(starttimestr, '%Y%m%d%H%M%S'))
    endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(endtimestr, '%Y%m%d%H%M%S'))

    # 判断是否有执行中的任务，若有则以任务的创建时间为准，并更新任务状态、文件路径
    record = recordSave(starttime, endtime, file, dstfile, "PBOSS订单-回退")

    # 文件迁移
    shutil.move(srcfile, dstfile)

    # 获取表头
    df_head = df.columns.values.tolist()

    # 文件数据入库
    for i in range(df.shape[0]):
        pbrollback = PbossOrderRollback()
        pbrollback.order_starttime = starttime
        pbrollback.order_endtime = endtime
        pbrollback.order_createtime = record.record_createtime
        for j in range(len(df_head)):
            if df_head[j] == "OWNERNAME":
                pbrollback.order_area = df.iloc[i, j]
            elif df_head[j] == "SERVICENAME":
                pbrollback.order_rbdesc = df.iloc[i, j]
            elif df_head[j] == "TYPE":
                pbrollback.order_type = df.iloc[i, j]
            elif df_head[j] == "COUNT(SERVICENAME)":
                pbrollback.order_number = df.iloc[i, j]
            print(pbrollback.order_area, df.iloc[i, j])
        pbrollback.save()
    return None

#记录入库函数
def recordSave(starttime, endtime, file, dstfile, type):
    # 判断是否有执行中的任务，若有则以任务的创建时间为准，并更新任务状态、文件路径
    record = PbossOrderRecord.objects.filter(record_starttime=starttime, record_endtime=endtime,
                                             record_result="执行中", record_type=type).first()
    if record:
        record.record_result = "成功"
        record.record_filedir = localfilebakdir + file
        record.save()
        return record
    else:
        createtime = datetime.now()

        # 新增新的记录
        newrecord = PbossOrderRecord()
        newrecord.record_type = type
        newrecord.record_starttime = starttime
        newrecord.record_endtime = endtime
        newrecord.record_createtime = createtime
        newrecord.record_mode = "自动生成"
        newrecord.record_result = "成功"
        newrecord.record_filedir = dstfile
        newrecord.save()
        return newrecord
