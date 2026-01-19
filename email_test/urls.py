from django.urls import path
from . import views

app_name = 'email_test'

urlpatterns = [
    path('send/', views.send_test_email, name='send_test_email'),
    path('send-html/', views.send_html_email, name='send_html_email'),
    path('config/', views.email_config_status, name='email_config_status'),
]
