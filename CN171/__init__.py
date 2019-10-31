#Celery相关
from __future__ import absolute_import, unicode_literals
from CN171.celery import app as celery_app
__all__ = ['celery_app']


#MySQL数据库相关
import pymysql
pymysql.install_as_MySQLdb()