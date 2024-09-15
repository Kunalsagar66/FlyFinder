from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('ping', Ping.as_view(), name='ping'),
    path('price', Price.as_view(), name='price'),
]
