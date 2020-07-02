from django.shortcuts import  render


def wiki(request, project_id):
    """ wiki的首页 """

    return render(request, 'wiki.html')