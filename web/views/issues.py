
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.forms.issues import IssuesModelForm, IssuesReplyModelForm, InviteModelForm
from web import models
import json
from utils.pagination import Pagination
from utils.encrypt import uid
from django.utils.safestring import mark_safe
import datetime
from django.urls import reverse

# 组合筛选小组件
class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request
    # 可迭代对象，生成筛选框
    def __iter__(self):
        # data_list是model里面的choices( (2,"处理中")， )
        for item in self.data_list:
            key = str(item[0])# 统一转化为字符串
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等，则选中
            # value_list是[1,2,3]
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)#减少参数
            else:
                value_list.append(key)#增加参数
            # 为自己生成URL
            # 在当前URL的基础上去增加一项或者减少一项
            query_dict = self.request.GET.copy() # 拷贝一份url的参数，status=1&age=19
            query_dict._mutable = True # query_dict允许被修改
            query_dict.setlist(self.name, value_list)
            # 筛选完成回到第一页
            if 'page' in query_dict:
                query_dict.pop('page')
            # 将{"status":[1,2,3],"xx",1}构造成status=1&status=2&status=3&xx=1
            param_url = query_dict.urlencode()
            # 没筛选时去掉url上的问号
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)
# 下拉框筛选
class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")

def issues(request, project_id):
    if request.method == "GET":
        # 根据URL做筛选，筛选条件（根据用户通过GET传过来的参数实现）
        # ?status=1&status=2&issues_type=1
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # [1,2]
            if not value_list:
                continue
            condition["{}__in".format(name)] = value_list
        """
        condition = {
            "status__in":[1,2],
            'issues_type__in':[1,]
        }
        """

        # 分页获取数据，filter接收字典
        queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)

        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        # 外键IssuesType
        project_issues_type = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')
        # 项目参与者
        project_total_user = [(request.tracer.project.creator_id, request.tracer.project.creator.username,)]
        join_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__username')
        project_total_user.extend(join_user)

        invite_form = InviteModelForm()

        context = {
            'form': form,
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': [
                {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
                {'title': "状态", 'filter': CheckFilter('status', models.Issues.status_choices, request)},
                {'title': "优先级", 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
                {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
            ]
        }
        return render(request, 'issues.html', context)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    """ 编辑问题 """
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    form = IssuesModelForm(request, issues_id, instance=issues_object)
    return render(request, 'issues_detail.html', {'form': form, "issues_object": issues_object})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """ 初始化操作记录 """

    # 判断是否可以评论和是否可以操作这个问题

    # 目前的判断是：只要能进入这个项目就能评论这个问题

    if request.method == "GET":
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)
        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }

        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    # 操作的问题的对象，更新的就是这个对象的数据
    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    post_dict = json.loads(request.body.decode('utf-8')) # 接收json数据的方法
    """
    {'name': 'subject', 'value': '好饿呀sdfasdf'}
    {'name': 'subject', 'value': ''}
    
    {'name': 'desc', 'value': '好饿呀sdfasdf'}
    {'name': 'desc', 'value': ''}
    
    {'name': 'start_date', 'value': '好饿呀sdfasdf'}
    {'name': 'end_date', 'value': '好饿呀sdfasdf'}
    
    {'name': 'issues_type', 'value': '2'}
    {'name': 'assign', 'value': '4'}
    """
    name = post_dict.get('name')
    value = post_dict.get('value')
    # 后面会用很多次，所以提取出来。
    def create_reply_record(content):
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.tracer.user,
        )
        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }
        return new_reply_dict
    #print(post_dict)
    # 拿到某个字段的对象，可以点出字段的参数，比如field_object.null判断是否允许为空
    field_object = models.Issues._meta.get_field(name)
    # 1. 数据库字段更新，以防黑客恶意篡改，不同字段有不同更新方式，分情况讨论
    # 1.1 文本
    if name in ["subject", 'desc', 'start_date', 'end_date']: # 文本的字段
        if not value: # value为空
            if not field_object.null: # 但是该字段不允许为空
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            setattr(issues_object, name, None) # 反射的知识点
            issues_object.save() # 将变更保存到数据库
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            setattr(issues_object, name, value)
            issues_object.save()
            # 记录：xx更为了value
            change_record = "{}更新为{}".format(field_object.verbose_name, value)
        # 在IssuesReply表中创建一条变更记录
        # 如果变更记录太长，不让它存那么长到数据库
        if len(change_record) > 40:
            change_record = change_record[0:40] + "..."
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.tracer.user,
        )
        # 与评论的数据一样，前端可以共用一个函数动态生成变更记录
        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }

        return JsonResponse({'status': True, 'data': new_reply_dict})
    # 1.2 ForeignKey字段（指派的话要判断是否创建者或参与者）
    if name in ['issues_type', 'module', 'parent', 'assign']:
        # 用户选择为空
        if not value:
            # 不允许为空,因为这提供的是select，所以如果提交的是空只能说明是黑客入侵
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            # 允许为空
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:  # 用户输入不为空
            # 判断这一步也是防黑客，如果正常选择，不会有问题
            # 判断指派必须是项目创建者或者参与者或为空（不指派）
            if name == 'assign':
                # 是否是项目创建者
                if value == str(request.tracer.project.creator_id): # 因为value是字符串
                    instance = request.tracer.project.creator
                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,
                                                                            user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    # 被入侵
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                setattr(issues_object, name, instance)# 这一句挺关键，instance是对象也行的
                issues_object.save()
                change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))  
            else:
                # 条件判断：用户选择的值，是该问题存在的外键的值。假如我的问题没有bug选项就不能选
                # 这都是防一手恶意篡改，正常操作不会有问题
        ################ 通过字段找到外键的表并筛选，rel ##########################
                instance = field_object.rel.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})

                setattr(issues_object, name, instance)
                issues_object.save()
                # 这一句非常巧妙，本来可以用instance.title什么的拿到你想显示的东西
                # 这个str(instance)直接调用了该对象的__str__方法
                change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # 1.3 choices字段
    if name in ['priority', 'status', 'mode']:
        selected_text = None
        for key, text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': "您选择的值不存在"})

        setattr(issues_object, name, value)
        issues_object.save()
        change_record = "{}更新为{}".format(field_object.verbose_name, selected_text)
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # 1.4 M2M字段
    if name == "attention":
        # {"name":"attention","value":[1,2,3]}
        # value不是列表类型
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': "数据格式错误"})
        # 指派为空
        if not value:
            issues_object.attention.set(value) #多对多m2m的更新方式
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            # values=["1",2,3,4]  ->   id是否是项目成员（参与者、创建者）
            # 获取当前项目的所有成员
            # 无论列表里是str或int统一转换成str
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
            # 获取选择的用户名
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                username_list.append(username)

            issues_object.attention.set(value) #多对多m2m的更新方式
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name, ",".join(username_list))

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    return JsonResponse({'status': False, 'error': "滚"})


def invite_url(request, project_id):
    """ 生成邀请码 """

    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建随机的邀请码
        2. 验证码保存到数据库
        3. 限制：只有创建者才能邀请
        """
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period', "无权创建邀请码")
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer.user
        form.save()

        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': random_invite_code})
        )

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    """ 访问邀请码 """
    current_datetime = datetime.datetime.now()

    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'invite_join.html', {'error': '邀请码不存在'})

    if invite_object.project.creator == request.tracer.user:
        return render(request, 'invite_join.html', {'error': '创建者无需再加入项目'})

    exists = models.ProjectUser.objects.filter(project=invite_object.project, user=request.tracer.user).exists()
    if exists:
        return render(request, 'invite_join.html', {'error': '已加入项目无需再加入'})

    # ####### 问题1： 最多允许的成员(要进入的项目的创建者的限制）#######
    # max_member = request.tracer.price_policy.project_member # 当前登录用户他限制

    # 是否已过期，如果已过期则使用免费额度
    max_transaction = models.Transaction.objects.filter(user=invite_object.project.creator).order_by('-id').first()
    if max_transaction.price_policy.category == 1:
        max_member = max_transaction.price_policy.project_member
    else:
        if max_transaction.end_datetime < current_datetime:
            free_object = models.PricePolicy.objects.filter(category=1).first()
            max_member = free_object.project_member
        else:
            max_member = max_transaction.price_policy.project_member

    # 目前所有成员(创建者&参与者）
    current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    current_member = current_member + 1
    if current_member >= max_member:
        return render(request, 'invite_join.html', {'error': '项目成员超限，请升级套餐'})

    # 邀请码是否过期？
    
    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})

    # 数量限制？
    if invite_object.count:
        if invite_object.use_count >= invite_object.count:
            return render(request, 'invite_join.html', {'error': '邀请码数据已使用完'})
        invite_object.use_count += 1
        invite_object.save()

    models.ProjectUser.objects.create(user=request.tracer.user, project=invite_object.project)

    # ####### 问题2： 更新项目参与成员 #######
    invite_object.project.join_count += 1
    invite_object.project.save()
    
    return render(request, 'invite_join.html', {'project': invite_object.project})