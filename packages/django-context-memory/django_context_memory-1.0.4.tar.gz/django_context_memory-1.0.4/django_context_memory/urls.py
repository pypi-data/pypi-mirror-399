"""
URL configuration for Django Context Memory web interface

Include these URLs in your project's urls.py:

    from django.urls import path, include

    urlpatterns = [
        ...
        path('context-memory/', include('django_context_memory.urls')),
    ]
"""

from django.urls import path
from . import views

app_name = 'django_context_memory'

urlpatterns = [
    path('', views.index, name='index'),
    path('action/start/', views.action_start, name='action_start'),
    path('action/end/', views.action_end, name='action_end'),
    path('action/build/', views.action_build, name='action_build'),
    path('action/build-all/', views.action_build_all, name='action_build_all'),
    path('status/', views.get_status, name='get_status'),
]
