from django.urls import path

from . import views

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('', views.index_view, name='index'),
]

