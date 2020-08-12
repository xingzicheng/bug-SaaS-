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
            "parent": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
        }
    
    def __init__(self, request, IssuesId=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 数据初始化

        # 1.获取当前项目所有的问题类型[ (1,"xx"), (2, "xx")]
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(
            project=request.tracer.project
        ).values_list('id', 'title')
        # 2.获取当前项目的所有模块
        module_list = [("","没有选中任何项"),]
        module_object_list = models.Module.objects.filter(
            project=request.tracer.project
        ).values_list("id", "title")
        module_list.extend(module_object_list)
        self.fields['module'].choices = module_list
        # 3.指派者和关注着
        # 数据库找到当前项目的 参与者 和 创建者
        total_user_list = [(request.tracer.project.creator_id, request.tracer.project.creator.username),]
        project_user_list = models.ProjectUser.objects.filter(
            project=request.tracer.project
        ).values_list('user_id', 'user__username')
        total_user_list.extend(project_user_list)

        self.fields['assign'].choices = [("", "不指派")] + total_user_list
        self.fields['attention'].choices = total_user_list

        # 4.当前项目自己创建的问题
        parent_list = [("", "没有选中任何项")]
        parent_object_list = models.Issues.objects.filter(
            project=request.tracer.project
        ).values_list("id", "subject")
        parent_list.extend(parent_object_list)
        # 解决bug：修改问题将自己作为父问题
        # 若传来了IssuesId，则说明是修改问题，将自己移除出父问题，否则是None，说明是新建问题
        if IssuesId:
            me = models.Issues.objects.filter(
            project=request.tracer.project,
            id=IssuesId
            ).values_list("id", "subject")
            #print(me[0])
            #print(parent_list)
            parent_list.remove(me[0])
        self.fields['parent'].choices = parent_list

class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']

class InviteModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'count']
    