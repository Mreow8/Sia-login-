from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    # Changed dashes to underscores to match login.js
    path('api/send_email_otp/', views.send_email_otp, name='send_otp'),
    path('api/verify_email_otp/', views.verify_email_otp, name='verify_otp'),
    path('api/report_failure/', views.handle_email_login, name='report_failure'), # Added to prevent JS error
    path('api/login/', views.handle_email_login, name='login'),
]