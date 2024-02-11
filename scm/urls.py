from django.urls import path

from scm import views


app_name = 'scm'

urlpatterns = [
    path('', views.receive_webhook),
]
