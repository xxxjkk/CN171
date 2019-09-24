from django.shortcuts import render

# Create your views here.
def taskManagement(request):
    return render(request, "background/task_management.html", locals())