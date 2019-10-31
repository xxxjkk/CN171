from django.shortcuts import render

# Create your views here.



#容量预测主函数
def capacity(request):
    return render(request, "aiops/capacity.html", locals())


#智能告警分析（PBOSS）主函数
def warningPboss(request):
    return render(request, "aiops/warningpboss.html", locals())