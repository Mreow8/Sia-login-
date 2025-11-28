from django.contrib import admin
from django.urls import path
from mainapp import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('api/send_email_otp/', views.send_email_otp, name='send_email_otp'),
    path('api/verify_email_otp/', views.verify_email_otp, name='verify_email_otp'),
    path('api/register/', views.complete_registration, name='complete_registration'),  # NEW
    path('api/report_failure/', views.report_failure, name='report_failure'),
    path('api/login/', views.handle_email_login, name='handle_email_login'),
]