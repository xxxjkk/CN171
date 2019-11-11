"""
Django settings for CN171 project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import pymysql
import os
try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = cp.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config/cn171.conf'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '42427w*ffn#8a&!@8bd*ia^j93&0$ufe#re*5dmt&&l^y-0jj5'

#设置浏览器关闭时session失效
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#设置登陆超时时长（10分钟）
SESSION_COOKIE_AGE = 60*10

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'CN171_account',
    'CN171_background',
    'CN171_cmdb',
    'CN171_config',
    'CN171_login',
    'CN171_monitor',
    'CN171_order',
    'CN171_crontab',
    'djcelery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CN171.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CN171.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (css, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


pymysql.install_as_MySQLdb()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get('DataBase', 'database'),
        'USER': config.get('DataBase', 'user'),
        'PASSWORD': config.get('DataBase', 'password'),
        'HOST': config.get('DataBase', 'host'),
        'PORT': config.getint('DataBase', 'port'),
    }
}

# 默认
STATIC_URL = '/static/'
# 项目根目录下的static文件夹
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
# 不能和STATIC_ROOT路径相同
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# 设置邮件域名
EMAIL_HOST = config.get('PBOSS', 'pboss_order_mail_host')
# 设置端口号，为数字
EMAIL_PORT = config.get('PBOSS', 'pboss_order_mail_host_port')
#设置发件人邮箱
EMAIL_HOST_USER = config.get('PBOSS', 'pboss_order_mail_inbox')
# 设置发件人 授权码
EMAIL_HOST_PASSWORD = config.get('PBOSS', 'pboss_order_mail_password')
# 设置是否启用安全链接
EMAIL_USER_TLS = True





# Broker配置，使用Redis作为消息中间件
BROKER_URL = config.get('Celery', 'celery_broker_url')
# BACKEND配置，使用Redis作为结果存储
CELERY_RESULT_BACKEND = config.get('Celery', 'celery_result_backend')
# 结果序列化方案
CELERY_RESULT_SERIALIZER = config.get('Celery', 'celery_result_serializer')
#设置时区
CELERY_TIMEZONE = config.get('Celery', 'celery_timezone')
#设置beat数据库
CELERYBEAT_SCHEDULER = config.get('Celery', 'celery_beat_scheduler')


