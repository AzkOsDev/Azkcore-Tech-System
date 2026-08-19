from django.shortcuts import render

def messages_view(request):
    return render(request, 'home/messages.html', {})

#@login_required
#def messages_view(request):
    # ---- Filtro por estado (?estado=todos|pendientes|atendidos) ----
    #estado_filtro = request.GET.get('estado', 'todos')

   # qs = ContactMessage.objects.all()  # ya viene ordenado por -creado gracias al Meta del modelo

   # if estado_filtro == 'pendientes':
  #      qs = qs.filter(atendido=False)
 #   elif estado_filtro == 'atendidos':
   #     qs = qs.filter(atendido=True)
    # 'todos' o cualquier otro valor -> sin filtro adicional

    # ---- Stat cards ----
    #total_count = ContactMessage.objects.count()
    #pendientes_count = ContactMessage.objects.filter(atendido=False).count()
   # atendidos_count = ContactMessage.objects.filter(atendido=True).count()

  #  inicio_semana = timezone.now() - timedelta(days=7)
   # semana_count = ContactMessage.objects.filter(creado__gte=inicio_semana).count()

    # ---- Paginación ----
    #paginator = Paginator(qs, 10)  # 10 mensajes por página, ajusta a gusto
    #page_number = request.GET.get('page')
    #page_obj = paginator.get_page(page_number)

    #context = {
    #    'messages': page_obj,          # el template itera sobre "messages"
    #    'page_obj': page_obj,
   #     'is_paginated': page_obj.has_other_pages(),
  #      'estado_filtro': estado_filtro,
   #     'total_count': total_count,
  #      'pendientes_count': pendientes_count,
  #      'atendidos_count': atendidos_count,
  #      'semana_count': semana_count,
  #  }

   # return render(request, 'home/messages.html', context)


#@login_required
#def contact_message_mark_atendido(request, pk):
#    if request.method == 'POST':
      #  msg = get_object_or_404(ContactMessage, pk=pk)
 #      msg.atendido = True
   #     msg.save(update_fields=['atendido'])
    #    django_messages.success(request, f'Mensaje de {msg.nombre} marcado como atendido.')
 #   return redirect(request.META.get('HTTP_REFERER', 'messages'))