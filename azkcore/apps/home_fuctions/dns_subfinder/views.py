from django.shortcuts import render

def dns_subfinder(request):
    return render(request, 'home/dns_subfinder.html')
