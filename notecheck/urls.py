from django.conf import settings
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('favicon.ico/', RedirectView.as_view(url=settings.STATIC_URL + 'notecheck/favicon.ico')),
    path('playnotepitch/', views.playnotepitch),
    path('', views.index, name='index'),
    path('<str:token>/', views.submission, name='submission'),
    path('<str:token>/<int:submission_id>/', views.submission, name='submission'),
]
