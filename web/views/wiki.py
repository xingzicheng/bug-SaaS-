from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from web.forms.wiki import WikiModelForm

from django.http import JsonResponse
from web import models


def wiki(request, project_id):
    """ wiki的首页 """
    wiki_id = request.GET.get('wiki_id')# 问号传参这样获取
    # 如果wiki_id合法才返回预览页面
    if not wiki_id or not wiki_id.isdecimal():
        # 没有传wiki_id时不返回任何数据，前端判断一下{% if wiki_object %}是否有值，
        # 注意一下：这在普通py程序不允许的，因为这个变量没定义，比如说：
        # if x：
        #    print（‘1’）  这个程序会报错x没有定义，但是render里没传值应该是当空值处理
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


def wiki_delete(request, project_id, wiki_id):# URL传参这样获取
    """删除文章"""
    #加入project_id以免删除别人的文章
    # 级联删除，删除父文章，由于子文章外键自关联父文章，所以子文章也将删除
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    url = reverse('wiki', kwargs={'project_id':project_id})
    return redirect(url)

def wiki_edit(request, project_id, wiki_id):
    """编辑文章"""
    wiki_object = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == "GET":
        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki_add.html',{'form':form})
    # instance 是初始化的值，data是更新的数据，因为有数据在instance中，所以不需要和新建一样传一个
    # form.instance.project = request.tracer.project
    form = WikiModelForm(request,data=request.POST, instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        preview_url = "{0}?wiki_id={1}".format(url, wiki_id)
        return redirect(preview_url)

