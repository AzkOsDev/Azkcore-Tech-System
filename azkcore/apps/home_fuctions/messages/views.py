from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone


@login_required
def messages_view(request):
    estado_filtro = request.GET.get('estado', 'todos')

    try:
        response = requests.get(
            f"{settings.API_BASE_URL}/api/messages/all/",
            headers={"X-Authorization": f"Bearer {settings.API_BEARER_TOKEN}"},
            timeout=5,
        )
        response.raise_for_status()
        all_messages = response.json().get("messages", [])
    except requests.RequestException:
        all_messages = []
        django_messages.error(request, "No se pudo conectar con la API de la Landing Page.")

    if estado_filtro == 'pendientes':
        filtered = [m for m in all_messages if not m.get('atendido')]
    elif estado_filtro == 'atendidos':
        filtered = [m for m in all_messages if m.get('atendido')]
    else:
        filtered = all_messages

    total_count = len(all_messages)
    pendientes_count = sum(1 for m in all_messages if not m.get('atendido'))
    atendidos_count = sum(1 for m in all_messages if m.get('atendido'))

    inicio_semana = timezone.now() - timedelta(days=7)
    semana_count = sum(
        1 for m in all_messages
        if datetime.fromisoformat(m['creado']) >= inicio_semana
    )

    context = {
        'messages': filtered,
        'is_paginated': False,
        'estado_filtro': estado_filtro,
        'total_count': total_count,
        'pendientes_count': pendientes_count,
        'atendidos_count': atendidos_count,
        'semana_count': semana_count,
    }

    return render(request, 'home/messages.html', context)


@login_required
def contact_message_mark_atendido(request, pk):
    if request.method == 'POST':
        try:
            response = requests.patch(
                f"{settings.API_BASE_URL}/api/messages/{pk}/mark-atendido/",
                headers={"X-Authorization": f"Bearer {settings.API_BEARER_TOKEN}"},
                timeout=5,
            )
            if response.status_code == 200:
                nombre = response.json().get("message", {}).get("nombre", "")
                django_messages.success(request, f'Mensaje de {nombre} marcado como atendido.')
            elif response.status_code == 404:
                django_messages.error(request, 'El mensaje no existe.')
            else:
                django_messages.error(request, 'No se pudo actualizar el mensaje.')
        except requests.RequestException:
            django_messages.error(request, 'No se pudo conectar con la API de la Landing Page.')

    return redirect(request.META.get('HTTP_REFERER', 'messages'))