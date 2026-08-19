from django.shortcuts import render

def scan_network_view(request):
    # Aquí puedes agregar la lógica para escanear la red
    return render(request, 'home/scan_network.html')
