from django.urls import path
from django.conf.urls import include,url
from django.contrib import admin
from CN171_login import views as loginviews
from django.views import static
from django.conf import settings

urlpatterns = [
    #Django的管理页面
    #path('admin/', admin.site.urls),
     url(r'^admin/', admin.site.urls),

    #登陆页面
      url(r'^$', loginviews.login, name='login'),
      url(r'^index/', loginviews.index, name='index'),
      url(r'^logout/', loginviews.logout, name='logout'),
      url(r'^login/', loginviews.login, name='login'),
      url(r'^loginnotice/', loginviews.loginNotice, name='loginnotice'),


     # url(r'^login/', include('CN171_login.urls')),
      url(r'^cmdb/', include('CN171_cmdb.urls')),
      url(r'^background/', include('CN171_background.urls')),
      url(r'^account/', include('CN171_account.urls')),
      url(r'^config/', include('CN171_config.urls')),
      url(r'^monitor/', include('CN171_monitor.urls')),
      url(r'^order/', include('CN171_order.urls')),
      url(r'^crontab/', include('CN171_crontab.urls')),
      url(r'^aiops/', include('CN171_aiops.urls')),

      url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static')
]
