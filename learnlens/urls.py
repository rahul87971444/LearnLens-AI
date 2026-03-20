from django.contrib import admin
from django.urls import path
from analyzer import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('download/', views.download_pdf, name='download_pdf'),
]
