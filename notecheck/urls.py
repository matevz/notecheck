from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:token>/', views.submission, name='submission'),
    path('<str:token>/<int:submission_id>/', views.submission, name='submission'),
]
