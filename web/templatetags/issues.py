from django.template import Library
from django.urls import reverse
from web import models

register = Library()

# id不足三位补全三位
@register.simple_tag
def string_just(num):
    if num < 100:
        num = str(num).rjust(3, "0")
    return "#{}".format(num)