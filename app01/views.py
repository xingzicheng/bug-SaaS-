from django.shortcuts import render, HttpResponse

# Create your views here.
import random
from utils.tencent.sms import send_sms_single
from django.conf import settings
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection

def send_sms(request):
    """发送短信"""
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not template_id:
        return HttpResponse('模板不存在')
    code = random.randrange(100000,999999)
    send_sms_single('1527182', 645945, [code, ])
    return HttpResponse('成功')


from app01 import models
class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号', validators=[RegexValidator(r'(1[3|4|5|6|7|8|9])\d{9}$')])
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')
    class Meta:
        model = models.UserInfo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' %(field.label)




def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form':form})


def index(request):
    # 去连接池中获取一个连接
    conn = get_redis_connection("default")
    conn.set('nickname', "武沛齐", ex=10)
    value = conn.get('nickname')
    value = value.decode(encoding="utf-8")
    print(value)
    return HttpResponse(value)