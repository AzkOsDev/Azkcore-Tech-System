from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import LogEntry


@login_required
def logs_view(request):
    query = request.GET.get("q", "").strip()
    nivel_filtro = request.GET.get("nivel", "todos")

    logs_qs = LogEntry.objects.select_related("usuario").all()

    if nivel_filtro and nivel_filtro != "todos":
        logs_qs = logs_qs.filter(nivel=nivel_filtro)

    if query:
        logs_qs = logs_qs.filter(
            Q(mensaje__icontains=query)
            | Q(ip__icontains=query)
            | Q(usuario__username__icontains=query)
            | Q(detalle__icontains=query)
            | Q(origen__icontains=query)
        )

    paginator = Paginator(logs_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "logs": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "query": query,
        "nivel_filtro": nivel_filtro,
    }
    return render(request, "home/logs.html", context)