from django import forms
from django.forms import widgets, models
from django.forms.widgets import *

from CN171_background.models import BgTaskManagement
from CN171_cmdb.models import HostPwdOprLog, CmdbHost, CmdbApp, CmdbAppCluster


class DetailLogForm(forms.ModelForm):
    class Meta:
        model = HostPwdOprLog
        fields = ('detail_log',)
        widgets={
            'detail_log': Textarea(attrs={'name':'detailLog', 'style':'width:1000px; height:300px', 'row':'100','maxlength':'255', 'id':'detailLog', 'class':'form-control', 'cols':'40','readonly':'readonly'}),
        }

#主机密码编辑页面
class HostPwdEditForm(forms.Form):
    modified_host_list_file = forms.FileField(label=u'选择要变更的主机列表文件', error_messages={'required':'请选择要变更的主机列表文件'})  #改成True有问题
    modified_host_user= forms.CharField(label=u'变更用户', error_messages={'required':'请输入要变更的用户','style':'color:red;'},
      widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width:200px;','placeholder': u'必填项'}))
    old_password = forms.CharField(label=u'原密码', error_messages={'required': '请输入原始密码'},
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width:200px;','placeholder': u'必填项'}))
    new_password1 = forms.CharField(label=u'新密码', error_messages={'required': '请输入新密码'},
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width:200px;','placeholder': u'必填项'}))
    new_password2 = forms.CharField(label=u'新密码', error_messages={'required': '请重复新输入密码'},
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width:200px;','placeholder': u'必填项'}))

    #验证两次密码是否一致
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if len(password1)<6:
            raise forms.ValidationError(u'密码必须大于6位')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次密码输入不一致')
        return password2



class NormalUserForm(forms.Form):
    username = forms.CharField()
    headImg = forms.FileField()

#主机表单页面
class CmdbHostForm(forms.ModelForm):
    class Meta:
        model= CmdbHost
        fields=('bg','cmdb_host_name','cmdb_host_type','cmdb_host_pod','cmdb_host_system','cmdb_host_busip','cmdb_host_manip','cmdb_host_cpu','cmdb_host_RAM','cmdb_host_local_disc','cmdb_host_outlay_disc','cmdb_host_status')

        widgets = {
            'bg': Select( attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必选项'}),
            'cmdb_host_name': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_type': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_pod': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_system': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_busip': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_manip': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_cpu': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_RAM': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_local_disc': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_outlay_disc': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'cmdb_host_status': Select(attrs={'class': 'form-control', 'style': 'width:530px;'}),
        }

#应用页面
class CmdbAppForm(forms.ModelForm):
    class Meta:
        model= CmdbApp
        fields=('cmdb_host','appNetmode','cmdbAppCluster','app_name','app_status')

        widgets = {
            'cmdb_host': Select( attrs={'class': 'form-control', 'style': 'width:530px;'}),
            'appNetmode': Select( attrs={'class': 'form-control', 'style': 'width:530px;'}),
            'cmdbAppCluster': Select(attrs={'class': 'form-control', 'style': 'width:530px;'}),
            'app_name': TextInput(attrs={'class': 'form-control', 'style': 'width:530px;', 'placeholder': u'必填项'}),
            'app_status': Select(attrs={'class': 'form-control', 'style': 'width:530px;'}),
        }