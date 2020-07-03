from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from web.forms.wiki import WikiModelForm

from django.http import JsonResponse
from web import models


def wiki(request, project_id):
    """ wiki的首页 """
    wiki_id = request.GET.get('wiki_id')
    # 如果wiki_id合法才返回预览页面
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')

    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()

    return render(request, 'wiki.html', {'wiki_object': wiki_object})

def wiki_add(request, project_id):
    """ wiki添加 """
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html', {'form': form})
    # POST
    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        # 判断用户是否已经选择父文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    return render(request, 'wiki_add.html', {'form': form})

def wiki_catalog(request, project_id):
    """ wiki目录 """

    # 获取当前项目所有的目录: data = QuerySet类型
    # data = models.Wiki.objects.filter(project=request.tracer.project).values_list("id", 'title', 'parent_id')
    data = models.Wiki.objects.filter(project=request.tracer.project).values("id", 'title', 'parent_id').order_by(
        'depth', 'id')
    # data = models.Wiki.objects.filter(project=request.tracer.project).values("id", 'title', 'parent_id')
    return JsonResponse({'status': True, 'data': list(data)})