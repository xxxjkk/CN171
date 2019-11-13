import datetime
from os.path import *
from django.http import HttpResponse

#导出txt文档
from CN171_tools.sftputils import path_not_exist_create


def export_txt(content1):
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = './download/txt/host_pwd_detail_log_' + now + '.txt'
    file = open(file_name, 'w')
    file.write(content1)
    file.close()
    # 获取上级目录绝对路径
    dir_path = dirname(dirname(abspath(__file__)))
    file_path=dir_path+"\download\\txt"
    return file_path

#导出txt文档
def export_txt(content1):
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    file_name = './download/txt/host_pwd_detail_log_' + now + '.txt'
    file = open(file_name, 'w')
    file.write(content1)
    file.close()
    # 获取上级目录绝对路径
    dir_path = dirname(dirname(abspath(__file__)))
    file_path=dir_path+"\download\\txt"
    return file_path

#写入txt文档
#在该filePath下将content1写入文件名为fileName的txt文档，
#filePath文件所在目录 例如：temp/cmdb/hostmgnt/status/20191108，fileName 例如：文件名 root_host_busip_ip.txt
#返回带绝对路径的文件名 D:/CN171/temp/cmdb/hostmgnt/status/20191108/host_busip_ip.txt 或者opt/app/.../..txt
def write_txt(content1, filePath, fileName):
    path_not_exist_create(filePath)
    file_name = filePath + fileName + '.txt'
    file = open(file_name, 'w')
    file.write(content1)
    file.close()
    # 获取上级目录绝对路径
    dir_path = dirname(dirname(abspath(__file__)))
    abspath_file_name= dir_path + "\\"+ file_name
    return abspath_file_name

#导出并下载txt文件
def export_download_txt(content1):
        response = HttpResponse(content_type='text/plain')
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        file_name = 'host_pwd_detail_log_' + now + '.txt'
        response['Content-Disposition'] = 'attachment;filename='+file_name
        contentArray=content1.split("\n")
        for contentRow in contentArray:
            #print(contentRow)
            response.write(contentRow)
            response.write("\r\n")
        return response

#字符串数组转换成int数组
def to_ints(all_ids):
    all_id_ints=[]
    if all_ids:
        for cmdb_id in all_ids.split(','):
            all_id_ints.append(int(cmdb_id))
    return all_id_ints

#访问二维元组，通过value获得key值 状态不对，默认停机
def get_tuple_key(tupleObj,tupleValue):
        for i in range(len(tupleObj)):
            for j in range(len(tupleObj[i])):
                if(tupleObj[i][1]==tupleValue):
                    return tupleObj[i][0]
                else:
                    return '3'

