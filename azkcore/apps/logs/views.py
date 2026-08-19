from django.shortcuts import render

def logs_view(request):
    return render(request, 'home/logs.html')