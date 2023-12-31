from django.urls import re_path as url
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from rest_framework_swagger.views import get_swagger_view

from config import settings

handler404 = 'web_view.view.httpresponse.handler404'
handler500 = 'web_view.view.httpresponse.handler500'
urlpatterns = [
    path('', include('web_view.urls')),
    path('api/', include('web_api.urls')),
    path('admin/', admin.site.urls),

    path("o/", include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'public/(?P<path>.*)$', serve, {'document_root': settings.STATIC_FILE_PATH}),
    url(r'^swagger/$', get_swagger_view(title='KAYI API'))
]
