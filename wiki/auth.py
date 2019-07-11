from django.http import HttpResponse,\
    HttpResponseRedirect,\
    HttpResponseNotFound,\
    HttpResponseBadRequest
from django.conf import settings
from django.template import loader
from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth import login


def register(request):
    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        try:
            user = User.objects.create_user(username, '', password)
            user.save()
            login(request, user)
            return HttpResponseRedirect('/')
        except Exception:
            template = loader.get_template('registration/register.html')
            return HttpResponse(
                template.render({'failed': True}, request),
                content_type='text/html'
            )
    else:
        template = loader.get_template('registration/register.html')
        return HttpResponse(
            template.render({'failed': False}, request),
            content_type='text/html'
        )
