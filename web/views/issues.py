
from django.shortcuts import render
from django.http import JsonResponse
from web.forms.issues import IssuesModelForm


def issues(request, project_id):
    if request.method == "GET":
        form = IssuesModelForm(request)
        return render(request, 'issues.html', {'form': form})

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})