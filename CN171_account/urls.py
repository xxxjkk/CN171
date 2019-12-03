from django.urls import path
from django.conf.urls import include,url
from CN171_account import views as userViews
urlpatterns = [
   url(r'^userManagement/', userViews.userManagement, name='userManagement'),
   url(r'^userAdd/', userViews.userAdd, name='userAdd'),
   url(r'^userDel/', userViews.userDel, name='userDel'),
   url(r'^userEdit/(?P<acc_user_id>\d+)/$', userViews.userEdit, name='userEdit'),
   url(r'^userStatusEdit/', userViews.userStatusEdit, name='userStatusEdit'),
   url(r'^userSearch/', userViews.userSearch, name='userSearch'),
   url(r'^distribute_permissions/', userViews.distribute_permissions, name='distribute_permissions'),
   url(r'^roleAdd/', userViews.roleAdd, name='roleAdd'),
   url(r'^permissionAdd/', userViews.permissionAdd, name='permissionAdd'),

]