#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/12/13 10:57
# @Author: zhaocy
# @File  : excelutil.py
# @Software: CN171
import os,shutil
import pandas
import time

from django.db.models import Q

from CN171_aiops import models
from CN171_aiops.models import DetectResult

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')

#文件路径和备份路径
localfiledir = config.get('AIopsCapacity', 'AIopsCapacity_result_path')

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