from django.shortcuts import render

def scan_web(request):
    return render(request, 'home/scan_web.html')