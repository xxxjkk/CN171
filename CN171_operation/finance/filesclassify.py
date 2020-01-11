#!/usr/bin/env python
#coding=utf-8
import os, sys, re
import importlib
import shutil
import time, datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count

from CN171_operation.models import *

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config = cp.RawConfigParser()
config.read(os.path.join(BASE_DIR, 'config/operation.conf'),encoding='utf-8')


importlib.reload(sys)

#获取当前文件目录下的指定类型的文件名称
def fileNameCollect(file_dir, flist, cnt, L, Lctime):
    if cnt==0:
        mlist=list(set(os.listdir(file_dir)).difference(set(flist)))
        cnt=1
    else:
        mlist=os.listdir(file_dir)
    for s in mlist:
        newdir = os.path.join(file_dir, s)  # 将文件名加入到当前文件路径后面
        if os.path.isfile(newdir):  # 如果是文件
            if os.path.splitext(newdir)[1] in ['.gz','.unl']:  # 如果文件是".pdb"后缀的
                L.append(newdir)
                Lctime.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.stat(newdir).st_ctime)))
        elif os.path.isdir(newdir) :  # 如果是路径
            fileNameCollect(newdir, flist, cnt, L, Lctime)  # 递归
    return L, Lctime

#整理文件
def filesClassify(pathtmp, path):
    file_path_tmp = pathtmp
    file_path = path
    flist_CN = config.get('Finance', 'finance_filetype_CN').split(', ')
    flist_EN = config.get('Finance', 'finance_filetype_EN').split(', ')
    arealist = config.get('Finance', 'finance_area').split(', ')
    areaidlist = config.get('Finance', 'finance_areaid').split(', ')
    mylist, myctimelist = fileNameCollect(file_dir=file_path_tmp, flist=flist_CN, cnt=0, L=[], Lctime=[])
    mylist_dict = dict(zip(mylist, myctimelist))

    #整理后的文件清单
    filelist = []
    flist_dict = dict(zip(flist_EN, flist_CN))
    print(flist_EN)
    print(flist_CN)
    print(flist_dict)
    area_dict = dict(zip(areaidlist, arealist))

    for file in mylist:
        #账务文件标识符
        isfinance = "false"

        #进行文件名分析
        filename = os.path.split(file)[1]
        filectime = mylist_dict.get(file)
        searchlist = fileNameAnalysis(filename)

        #判断列表是否均为None（以此判断文件是否属于13类文件之一）
        if list(filter(None, searchlist)):
            isfinance = 'true'
            for index in range(len(searchlist)):
                searchObj = searchlist[index]
                if searchObj:
                    if index == 0 or index == 12:
                        # 若为“缴费”或“个人代付”类型，截取对应位置的字段序号
                        index_type = 2
                        index_be = 1
                        index_date = 3
                        index_cycle = 4
                    else:
                        # 其他类型采用统一位置的字段序号
                        index_type = 1
                        index_be = 4
                        index_date = 2
                        index_cycle = 3
                    #类型
                    file_type_EN = searchObj.group(index_type).lower()
                    print(file_type_EN)
                    file_type_CN = flist_dict.get(file_type_EN)
                    print(file_type_CN)
                    #省份，如100
                    file_beid = searchObj.group(index_be)
                    file_be = area_dict.get(file_beid)
                    #日期，如20191201
                    file_billdate = searchObj.group(index_date)
                    #月期，如201912
                    file_billmonth = searchObj.group(index_cycle)

                    #账期
                    if file_type_EN in ['payment', 'ar_apply_detail', 'ar_transfer']:
                        #日文件类型
                        if file_billdate[-2:] == '01':
                            #每月第1天需要月份减1
                            tmp = datetime.datetime.strptime(file_billmonth[0:4] + '-' + file_billmonth[-2:], "%Y-%m")
                            file_billcycle = datetime.datetime.strftime(tmp - relativedelta(months=1), "%Y-%m")
                        else:
                            file_billcycle = file_billmonth[0:4] + '-' + file_billmonth[-2:]
                    else:
                        #月文件类型
                        if (file_type_EN in ['ar_invoice_detail']) and (file_beid not in ['371']):
                            file_billcycle = file_billmonth[0:4] + '-' + file_billmonth[-2:]
                        else:
                            tmp = datetime.datetime.strptime(file_billmonth[0:4] + '-' + file_billmonth[-2:], "%Y-%m")
                            file_billcycle = datetime.datetime.strftime(tmp - relativedelta(months=1), "%Y-%m")

                    #路径添加文件类型中文
                    patha = os.path.join(file_path, flist_CN[index])
                    #路径添加账期
                    pathb = os.path.join(patha, file_billcycle)
                    continue
        else:
            pathb = os.path.join(file_path, '其他')
        dstfile = os.path.join(pathb, filename)
        if not os.path.exists(pathb):
            print(u'目录%s不存在，新建目录！' %pathb)
            os.makedirs(pathb)
        else:
            if os.path.exists(dstfile):
                print(u'文件%s已存在，进行覆盖更新！' %dstfile)
        #文件迁移
        shutil.move(file, dstfile)
        filelist.append(dstfile)

        #若为账务文件，则进行数据入库
        if isfinance == 'true':
            #CMIOT账务文件管理表数据入库
            try:
                finance = OprFinance.objects.get(opr_area=file_be, opr_cycle=file_billcycle)
            except ObjectDoesNotExist:
                finance = None
                print('区域：%s  账期：%s  未找到账务文件管理表数据，新增数据！' %(file_be, file_billcycle))
            except MultipleObjectsReturned:
                print('区域：%s  账期：%s  存在多条相同条件账务文件管理表数据，存在异常，不进行处理！' %(file_be, file_billcycle))
                continue
            if finance:
                finance.opr_check_result = '尚未校验'
            else:
                finance = OprFinance()
                finance.opr_area = file_be
                finance.opr_cycle = file_billcycle
                finance.opr_check_result = '尚未校验'
            #数据保存
            finance.save()

            #CMIOT账务文件详情表数据入库
            try:
                filedetail = OprFinanceFiledetail.objects.get(opr_finance_filedetail_name = filename)
            except ObjectDoesNotExist:
                filedetail = None
                print(u'文件%s数据未入库，新增数据！' %filename)
            except MultipleObjectsReturned:
                print(u'文件%s存在多条相同数据，存在异常，不进行处理！' %filename)
                continue
            if filedetail:
                filedetail.opr_finance_filedetail_dir = pathb
            else:
                filedetail = OprFinanceFiledetail()
                print(filename)
                filedetail.opr_finance_filedetail_name = filename
                print(file_type_CN)
                filedetail.opr_finance_filedetail_type = file_type_CN
                print(filectime)
                filedetail.opr_finance_filedetail_createtime = filectime
                filedetail.opr_finance_filedetail_thistime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                filedetail.opr_finance_filedetail_num = 1
                filedetail.opr_finance_filedetail_check = '尚未校验'
                print(pathb)
                filedetail.opr_finance_filedetail_dir = pathb
                filedetail.save()

            #CMIOT账务稽核表数据入库
            try:
                financereco = OprFinanceReco.objects.get(opr_finance = finance)
            except ObjectDoesNotExist:
                financereco = None
                print(u'区域：%s  账期：%s  未找到稽核表数据，新增数据！' %(file_be, file_billcycle))
            except MultipleObjectsReturned:
                print(u'区域：%s  账期：%s  存在多条相同条件稽核表数据，存在异常，不进行处理！' %(file_be, file_billcycle))
                continue
            if financereco is None:
                financereco = OprFinanceReco()
                financereco.opr_finance = finance
                financereco.opr_finance_reco_result = '未启动'
                financereco.opr_finance_reco_file = '-'

            #关联外键
            filedetail.opr_finance = finance

            #数据保存
            filedetail.save()

            #统计本次文件更新后账务文件管理表的文件数量
            count = OprFinance.objects.filter(opr_area=file_be, opr_cycle=file_billcycle,
                                      file__opr_finance_filedetail_type=file_type_CN).annotate(
                                                    num=Count('file__opr_finance_filedetail_id'))

            #反射机制，动态访问对象属性，效果等同于finance.opr_payment = count[0].num
            if hasattr(finance, 'opr_'+file_type_EN):
                setattr(finance, 'opr_'+file_type_EN, count[0].num)

            #数据保存
            finance.save()
            financereco.save()

    return filelist


def fileNameAnalysis(filename):
    # 缴费
    searchObj1 = re.search(r'BOSS(\d{3})_(Payment)_((\d{6})\d{2})\d{6}_CTBS_C\d{3}.unl', filename, re.M | re.I)
    # 欠费
    searchObj2 = re.search(r'cbs_(ar_invoice_detail_owe)_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 调账
    searchObj3 = re.search(r'cbs_(ar_adjustment)_all_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 销账
    searchObj4 = re.search(r'cbs_(ar_apply_detail)_all_((\d{6})\d{2}?)_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 余额
    searchObj5 = re.search(r'cbs_(cm_acct_balance)_all_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 赠费
    searchObj6 = re.search(r'cbs_(bb_bill_charge_bonus)_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 账单
    searchObj7 = re.search(r'cbs_(ar_invoice_detail)_all_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 账户
    searchObj8 = re.search(r'cbs_(bc_acct)_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 呆坏账
    searchObj9 = re.search(r'cbs_(ar_writeoff)_all_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 解挂账
    searchObj10 = re.search(r'cbs_(ar_hunglog)_all_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 转账
    searchObj11 = re.search(r'cbs_(ar_transfer)_all_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 分摊
    searchObj12 = re.search(r'cbs_(ar_invoice_prorate)_((\d{6})\d{2})_\d*_(\d{3})_\d*_\d{5}.unl', filename, re.M | re.I)
    # 个人代付
    searchObj13 = re.search(r'BOSS(\d{3})_(UnifyPayment)_((\d{6})\d{2})\d{6}_CTBS_C\d{3}.unl', filename, re.M | re.I)

    # 生成列表
    searchlist = [searchObj1, searchObj2, searchObj3, searchObj4, searchObj5, searchObj6, searchObj7,
                  searchObj8, searchObj9, searchObj10, searchObj11, searchObj12, searchObj13]

    return searchlist