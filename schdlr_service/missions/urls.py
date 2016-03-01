from django.conf.urls import url, include

from . import views

urlpatterns = [
     url(r'^missions', views.MissionControlAPIView.as_view()),
]