
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

import time
from web.forms.project import ProjectModelForm
from web import models
from utils.tencent.cos import create_bucket
from xpinyin import Pinyin
from qcloud_cos.cos_exception import CosClientError


def project_list(request):
    """ 项目列表 """
    if request.method == "GET":
        # GET请求查看项目列表
        """
        1. 从数据库中获取两部分数据
            我创建的所有项目：已星标、未星标
            我参与的所有项目：已星标、未星标
        2. 提取已星标
            列表 = 循环 [我创建的所有项目] + [我参与的所有项目] 把已星标的数据提取

        得到三个列表：星标、创建、参与
        """
        project_dict = {'star': [], 'my': [], 'join': []}

        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                #获取星标项目到底是我创建的还是参与的，使取消星标回到正确的位置
                project_dict['star'].append({"value": row, 'type': 'my'})
            else:
                project_dict['my'].append(row)

        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({"value": item.project, 'type': 'join'})
            else:
                project_dict['join'].append(item.project)
        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})

    # POST，对话框的ajax添加项目。
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():

        name = form.cleaned_data['name']
        p = Pinyin()
        name_pinyin = p.get_pinyin(name)
        # 1. 为项目创建一个桶
        bucket = "{}-{}-{}-1302500805".format(name_pinyin,
                                              request.tracer.user.mobile_phone, str(int(time.time())))
        region = 'ap-nanjing'
        try:
            create_bucket(bucket, region)
        except CosClientError as e:
            # form.errors是一个对象：{ "name" : [ "字段不能为空",  ] },所以给它构造成这样就可以模拟raise ValidationError
            form.errors['name'] = ["项目名只能是数字字母和“-”"]
            return JsonResponse({'status': False, 'error': form.errors})

        # 验证通过：项目名、颜色、描述 + creator谁创建的项目？
        form.instance.bucket = bucket
        form.instance.region = region
        form.instance.creator = request.tracer.user
        # 创建项目
        form.save()
        return JsonResponse({'status': True})
    # form.errors传给前端是对象，但输出的时候是<ul>标签字符串，因为内部的方法将它转化了
    return JsonResponse({'status': False, 'error': form.errors})



def project_star(request, project_type, project_id):
    """ 星标项目 """
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
        return redirect('project_list')

    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
        return redirect('project_list')

    return HttpResponse('请求错误')


def project_unstar(request, project_type, project_id):
    """ 取消星标 """
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=False)
        return redirect('project_list')

    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=False)
        return redirect('project_list')

    return HttpResponse('请求错误')