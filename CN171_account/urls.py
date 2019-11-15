from django.urls import path
from django.conf.urls import include,url
from CN171_account import views as userViews
urlpatterns = [

   url(r'^userManagement/', userViews.userManagement, name='userManagement'),
   url(r'^userAdd/', userViews.userAdd, name='userAdd'),
   url(r'^userDel/', userViews.userDel, name='userDel'),
   url(r'^userEdit/', userViews.userEdit, name='userEdit'),
]
