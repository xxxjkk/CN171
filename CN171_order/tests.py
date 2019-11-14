# -*- coding:utf-8 -*-
import poplib
import smtplib
from django.shortcuts import render

class MailManager(object):
    def __init__(self):
        self.popHost = 'pop.163.com'
        self.smtpHost = 'smtp.163.com'
        self.port = 25
        self.userName = 'pbosspatrol@163.com'
        self.passWord = 'pb123456'
        self.login()
        self.configMailBox()

    # 登录邮箱
    def login(self):
        try:
            self.mailLink = poplib.POP3_SSL(self.popHost)
            self.mailLink.set_debuglevel(0)
            self.mailLink.user(self.userName)
            self.mailLink.pass_(self.passWord)
            self.mailLink.list()
            print(u'login success!')
        except Exception as e:
            print(u'login fail! ' + str(e))
            quit()

    # 获取邮件
    def retrMail(self):
        try:


            mail_list = self.mailLink.list()[1]
            if len(mail_list) == 0:
                return None
            mail_info = mail_list[0].split(' ')
            number = mail_info[0]
            mail = self.mailLink.retr(number)[1]
            self.mailLink.dele(number)

            subject = u''
            sender = u''
            for i in range(0, len(mail)):
                if mail[i].startswith('Subject'):
                    subject = mail[i][9:]
                if mail[i].startswith('X-Sender'):
                    sender = mail[i][10:]
                content = {'subject': subject, 'sender': sender}
                return content
        except Exception as e:
            print(str(e))
            return None

    def configMailBox(self):
        try:
            self.mail_box = smtplib.SMTP(self.smtpHost, self.port)
            self.mail_box.login(self.userName, self.passWord)
            print(u'config mailbox success!')
        except Exception as e:
            print(u'config mailbox fail! ' + str(e))
            quit()

if __name__ == '__main__':
    mailManager = MailManager()
    print("test1")
    mail = mailManager.retrMail()
    print("test2")
    if mail != None:
        print("test3")
        print(mail)
    print("test4")

#测试函数
def test(request):
    mailManager = MailManager()
    print("test1")
    mail = mailManager.retrMail()
    print("test2")
    if mail != None:
        print("test3")
        print(mail)
    print("test4")
    return render(request, "test.html")
