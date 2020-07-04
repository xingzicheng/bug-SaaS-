from django import forms

from web import models
from web.forms.bootstrap import BootStrapForm


class WikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ['project', 'depth', ]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 找到想要的字段把他绑定显示的数据重置
        # 数据 = 去数据库中获取 当前项目所有的wiki标题
        total_data_list = [("", "- - -"), ]
        data_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        # 使用choices可以改变django自动生成form所展示的内容
        # 并且自动生成 value=id，选项为title
        self.fields['parent'].choices = total_data_list