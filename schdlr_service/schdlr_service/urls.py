"""schdlr_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.authtoken import views as rest_auth_views


API_VERSION = 'v1'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    # Django REST Browsable API auth interface
    url(r'^api/' + API_VERSION + '/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    # Django REST Token Endpoint
    url(r'^api/' + API_VERSION + '/token', rest_auth_views.obtain_auth_token)
    
]
