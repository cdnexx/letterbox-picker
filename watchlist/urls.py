from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('user/<str:username>', views.index_page),
    path('get/user', views.get_username, name='get_username')
]
