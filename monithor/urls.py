from django.urls import path

from . import views

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('about/', views.about_view, name='about'),
    path('unhandled/', views.unhandled_view, name='unhandled'),
    path('', views.index_view, name='index'),
]

