# apps/passwordanalyzer/views.py
import hashlib
import json

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import PasswordAnalysisLog


@login_required
def password_analyzer_view(request):
    historial = PasswordAnalysisLog.objects.filter(creado_por=request.user)[:5]
    return render(request, 'home/password_analyzer.html', {'historial': historial})


@login_required
@require_POST
@csrf_protect
def check_breach(request):
    """
    Verifica si una contraseña aparece en filtraciones conocidas usando
    el modelo k-anonymity de HaveIBeenPwned: solo enviamos los primeros
    5 caracteres del hash SHA1, nunca la contraseña ni el hash completo.
    """
    data = json.loads(request.body)
    password = data.get('password', '')

    if not password:
        return JsonResponse({'error': 'No se envió contraseña'}, status=400)

    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    try:
        response = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return JsonResponse({'error': 'No se pudo consultar el servicio de filtraciones'}, status=503)

    filtrada = False
    veces_vista = 0
    for line in response.text.splitlines():
        hash_suffix, count = line.split(':')
        if hash_suffix == suffix:
            filtrada = True
            veces_vista = int(count)
            break

    return JsonResponse({'filtrada': filtrada, 'veces_vista': veces_vista})


@login_required
@require_POST
@csrf_protect
def save_analysis(request):
    """Guarda solo las métricas del análisis, nunca la contraseña."""
    data = json.loads(request.body)

    PasswordAnalysisLog.objects.create(
        longitud=data.get('longitud', 0),
        tiene_mayusculas=data.get('tiene_mayusculas', False),
        tiene_minusculas=data.get('tiene_minusculas', False),
        tiene_numeros=data.get('tiene_numeros', False),
        tiene_simbolos=data.get('tiene_simbolos', False),
        entropia_bits=data.get('entropia_bits', 0),
        fortaleza=data.get('fortaleza', 'muy_debil'),
        fue_filtrada=data.get('fue_filtrada'),
        creado_por=request.user,
    )
    return JsonResponse({'ok': True})