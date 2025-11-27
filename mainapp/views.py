from django.conf import settings
from django.shortcuts import render

def login_page(request):
    return render(request, "login.html", {"firebase_config": settings.FIREBASE_CONFIG})
