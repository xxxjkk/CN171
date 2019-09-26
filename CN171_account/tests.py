from django.test import TestCase

# Create your tests here.
import os
from django.core.paginator import Paginator

objects=['john', 'paul', 'george', 'ringo', 'lucy', 'meiry', 'checy', 'wind', 'flow', 'rain']
p = Paginator(objects, 3)   #实例化一个分页器，获得分页器 3条数据为一页，实例化分页对象
print(p.count )   #10 对象总共10个元素
print(p.num_pages)  #对象可分4页
print(p.page_range)  #xrang(1,5) 对象页的可迭代范围

page1=p.page(1) #取第一页
print(page1.object_list)  #第一页对象的列表【'jhon', 'paul', 'george'】
print(page1.number)  #当前页的页码 1

page2=p.page(2) #取第二页
print(page2.object_list)  #第一页对象的列表【'ringo', 'lucy', 'meiry'】
print(page2.number)  #当前页的页码 2

print(page1.has_previous()) #第一页是否有前一页
print(page1.has_other_pages())  #第一页对象是否有其他页  true

print(page2.has_next()) #第2页是否有下一页
print(page2.previous_page_number()) # 第2页的前一页的页码
print(page2.next_page_number())  #第2页下一页的页码  true

print(page2.start_index()) #第二页对象的元素开始索引
print(page2.end_index()) #第二页对象元素的结束索引