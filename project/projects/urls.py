from django.urls import path
from .views import base_views, map_views

app_name = 'prj'

# 빈 url로 요청이 온다면, views 에 index를 연결해줄것이다.
urlpatterns = [
    # base_views.py
    path("", base_views.page, name="page"),
    path("data/",base_views.data,name="data"),
    path("about/",base_views.about,name="about"),
    path("data/",base_views.data,name="data"),

    # map_views.py
    path('map/',
         map_views.map, name='map'),
    path('map_detail/',
         map_views.map_detail, name='map_detail'),
]
