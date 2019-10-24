from django.contrib import admin
from django.urls import path, include
from wikirace import settings


urlpatterns = [
    # path('admin/', admin.site.urls),
    path(settings.ROOT_PATH, include('wiki.urls'))
]
