# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tasks_index, name='home'),
    
]
