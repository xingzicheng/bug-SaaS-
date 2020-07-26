from django import forms
from web.forms.bootstrap import BootStrapForm
from web import models

class IssuesModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            # 加上selectpicker样式就能变成选择框
            # "data-live-search": "true" 添加搜索框
            # 同理："data-actions-box": "true" 添加全选
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple( # 多选下拉框
                attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
        }