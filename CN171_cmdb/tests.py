from django.test import TestCase
from CN171_cmdb.tasks import refreshHostStatus
# Create your tests here.
from os.path import *
import os,sys

# 获取当前目录绝对路径
dir_path = dirname(abspath(__file__))
print('当前目录绝对路径:', dir_path)

# 获取上级目录绝对路径
dir_path = dirname(dirname(abspath(__file__)))
print('上级目录绝对路径:', dir_path)

print(os.getcwd()) #“C:\test”，取的是起始执行目录

print(sys.path[0]) #“C:\test\getpath”，取的是被初始执行的脚本的所在目录

print(os.path.split(os.path.realpath(__file__))[0]) #“C:\test\getpath\sub”，取的是file所在文件sub_path.py的所在目录

a='12,12,23,45,34,23'
print(type(a))
print(a)
print(a.replace(",","\n"))





