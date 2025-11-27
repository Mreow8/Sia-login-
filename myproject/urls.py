from django.contrib import admin
from django.urls import path, include  # <-- Make sure 'include' is imported!

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line tells Django: "For everything else, look inside mainapp/urls.py"
    path('', include('mainapp.urls')), 
]