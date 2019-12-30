from django import template
from django.conf import settings

register = template.Library()


def href(val):
    return '/' + settings.ROOT_PATH[:-1] + val


register.filter('href', href)
