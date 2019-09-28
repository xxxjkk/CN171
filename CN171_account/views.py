from django.shortcuts import render
from CN171_login import models
from CN171_background.api import pages

# Create your views here.

def userManagement(request):
    user_List = models.User.objects.all()
    p, page_objects, page_range, current_page, show_first, show_end, end_page, page_len = pages(user_List, request)
    return render(request, "account/user_management.html", locals())