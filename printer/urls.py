from django.urls import path
from . import views

urlpatterns = [
    path('shome', views.shapes_home, name='shome'),
]
