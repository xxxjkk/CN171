from django import forms
from django.forms import widgets
from django.forms.widgets import *
from CN171_cmdb.models import HostPwdOprLog


class DetailLogForm(forms.ModelForm):
    class Meta:
        model = HostPwdOprLog
        fields = ('detail_log',)
        widgets={
            'detail_log': Textarea(attrs={'name':'detailLog', 'style':'width:1000px; height:300px', 'row':'100','maxlength':'255', 'id':'detailLog', 'class':'form-control', 'cols':'40','readonly':'readonly'}),
        }

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
