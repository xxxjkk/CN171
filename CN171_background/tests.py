from filecmp import cmp

from django.test import TestCase

# Create your tests here.
from CN171_tools.common_api import get_tuple_key

HOST_STATUS = (
    (str(1), u"正常"),
    (str(2), u"异常"),
    (str(3), u"停机"),
    (str(4), u"启动中"),
)
#元组的使用
print(type(HOST_STATUS))
print(HOST_STATUS[1][1])
print(len(HOST_STATUS))
print('异常' in HOST_STATUS[1])
print(max(HOST_STATUS))
print(min(HOST_STATUS))
for i in range(len(HOST_STATUS)):
    print(i)



print(get_tuple_key(HOST_STATUS,'正常'))