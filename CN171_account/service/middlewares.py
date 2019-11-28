from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, HttpResponse
import re
class PermissionMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        # 设置白名单放行
        for reg in ["/login/", "/admin/*","/logout/","/index/"]:
            ret = re.search(reg, request.path)
            if ret:
                return None

        # 检验是否登录
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/login/')

        # 检验权限
        permission_list = request.session.get('permission_list')
        for reg in permission_list:
            reg = '^%s$' % reg
            ret = re.search(reg, request.path)
            if ret:
                return None
        return HttpResponse('无权访问')