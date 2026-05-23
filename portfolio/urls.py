from django.urls import path
from portfolio.views import index, project_detail

urlpatterns = [
    path('', index, name="home"),
    path('<slug:project_slug>/', project_detail, name='project-detail'),
]
