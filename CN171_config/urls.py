from django.urls import path
from django.conf.urls import include,url
from CN171_config import views as configViews

urlpatterns = [

    url(r'^config_management/', configViews.configManagement, name='configManagement'),
]
