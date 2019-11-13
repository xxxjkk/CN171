#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2019/10/14 9:56
# @Author: zhulong
# @File  : mailutils.py
# @Software: CN171

import os
import time
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from django.shortcuts import render

# 引入发送邮件的模块
from django.core.mail import send_mail

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

#读取配置文件
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'),encoding='utf-8')

#PBOSS文件路径和备份路径
pboss_mail_inbox = config.get('PBOSS', 'pboss_order_mail_inbox')
pboss_mail_outbox = config.get('PBOSS', 'pboss_order_mail_outbox')
pboss_mail_user = config.get('PBOSS', 'pboss_order_mail_user')
pboss_mail_password = config.get('PBOSS', 'pboss_order_mail_password')
filedir = config.get('PBOSS', 'pboss_order_local_filedir')


#PBOSS订单生成函数（通过邮件方式）
def pbossOrderMakebyMail(type, starttime, endtime):
    content = ""
    starttime = time.strftime('%Y/%m/%d %H:%M:%S', time.strptime(starttime, '%Y-%m-%d %H:%M:%S'))
    endtime = time.strftime('%Y/%m/%d %H:%M:%S', time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))

    #根据不同类型执行不同的生成命令
    if type == "状态":
        topic = "订单观察状态 " + starttime + "-" + endtime
        exec_result = sendEmail(topic, content, pboss_mail_inbox, pboss_mail_outbox)
    elif type == "节点":
        topic = "订单观察节点 " + starttime + "-" + endtime
        exec_result = sendEmail(topic, content, pboss_mail_inbox, pboss_mail_outbox)
    elif type == "回退":
        topic = "订单观察回退 " + starttime + "-" + endtime
        print(topic)
        print(content)
        exec_result = sendEmail(topic, content, pboss_mail_inbox, pboss_mail_outbox)
    else:
        print("未找到对应类型！")
        return "失败"
    print(exec_result)
    return exec_result


#发送邮件函数
def sendEmail(topic, content, frommail, tomail):
    # 值1：  邮件标题   值2： 邮件主体
    # 值3： 发件人      值4： 收件人
    res = send_mail(topic,
                    content,
                    frommail,
                    [tomail])
    if res == 1:
        return "成功"
    else:
        print(res)
        return "失败"


#邮件下载主函数
def retrMail():
    # 连接到POP3服务器
    server = poplib.POP3("pop.163.com")
    # 可以打开或关闭调试信息
    # server.set_debuglevel(1)
    # 可选:打印POP3服务器的欢迎文字
    print(server.getwelcome())
    # 身份认证
    server.user(pboss_mail_user)
    server.pass_(pboss_mail_password)
    # stat()返回邮件数量和占用空间
    print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似['1 82923', '2 2184', ...]
    print(mails)


    # 循环获取最新的邮件，读取后进行删除, 注意索引号从最大（即最新）开始
    mailsum = len(mails)
    for i in range(mailsum):
        index = mailsum - i
        print("-------------------邮件编号：" + str(index) + "   Start-------------------")
        resp, lines, octets = server.retr(index)

        #对lines中的每个元素进行bytes到str的转换，否则将无法进行后续处理
        lines_str = []
        for line in lines:
            str(line, encoding='utf-8')
            line_str = bytes.decode(line)
            lines_str.append(line_str)

        # lines存储了邮件的原始文本的每一行,可以获得整个邮件的原始文本
        msg_content = '\r\n'.join('%s' %id for id in lines_str)
        # 稍后解析出邮件
        msg = Parser().parsestr(msg_content)
        result = print_info(msg)
        # 可以根据执行情况，通过邮件索引从服务器删除邮件
        if result == "成功":
            server.dele(index)
            print("邮件下载成功，删除邮件！")
        print("-------------------邮件编号：" + str(index) + "   End-------------------")

    # 关闭连接
    server.quit()

    return "成功"

# indent用于缩进显示
def print_info(msg, indent=0):
    #获取邮件头
    if indent == 0:
        # 邮件的From, To, Subject存在于根对象上
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    # 需要解码Subject字符串
                    value = decode_str(value)
                else:
                    # 需要解码Email地址
                    hdr, adr = parseaddr(value)
                    name = decode_str(hdr)
                    addr = decode_str(adr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % (' ' * indent, header, value))
    if (msg.is_multipart()):
        # 如果邮件对象是一个MIMEMultipart
        # get_payload()返回list，包含所有的子对象
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            # print('%spart %s' % ('   ' * indent, n))
            print('%s--------------------' % ('   ' * indent))
            # 递归打印每一个子对象
            result = print_info(part, indent + 1)
    else:
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type=='text/html':
            # 纯文本或HTML内容
            content = msg.get_payload(decode=True)
            # 要检测文本编码
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            result = "成功"
            print('%sText: %s' % ('   ' * indent, content + '...'))
        else:
            # 不是文本,作为附件处理
            print("%s-------------------------Attachment  Start---------------------------" % ('   ' * indent))

            j = 0
            attachment_files = []
            for part in msg.walk():
                j = j + 1
                filename = part.get_filename()
                #如果是GBK格式则进行解码
                if 'GBK' in filename:
                    filename = decode_str(filename)

                if os.path.exists(filedir + filename):
                    print("%s文件《%s》在本地目录已存在，暂不下载！" % ('      ' * indent, filename))
                    result = "失败"
                else:
                    # 保存附件到下载目录
                    if filename:
                        data = part.get_payload(decode=True)
                        att_file = open(filedir + filename, 'wb')
                        attachment_files.append(filename)
                        att_file.write(data)
                        att_file.close()
                        print("%s《%s》下载完成！ 保存路径为：%s" % ('      ' * indent, filename, filedir))
                    result = "成功"
            print("%s-------------------------Attachment      End---------------------------" % ('   ' * indent))
    return result


#编码函数
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

#检测编码函数
def guess_charset(msg):
    # 先从msg对象获取编码
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


#测试函数
def test(request):
    retrMail()
    return render(request, "test.html")