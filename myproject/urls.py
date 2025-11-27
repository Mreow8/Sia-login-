from django.contrib import admin
from django.urls import path
from mainapp import views 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_page, name='home'),  # Homepage
]
