from django.conf.urls import   url
from django.contrib import admin
from djangoapp.views import index
admin.autodiscover()

urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^admin/', admin.site.urls),
]
