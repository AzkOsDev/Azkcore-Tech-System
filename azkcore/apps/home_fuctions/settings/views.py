from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


@login_required
def settings_view(request):
    if request.method == 'POST':
        user = request.user

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')

        # --- Validar username ---
        if not username:
            messages.error(request, 'El nombre de usuario no puede estar vacío.')
            return redirect('settings')

        if username != user.username and User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso.')
            return redirect('settings')

        # --- Validar email ---
        if email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'Ese correo ya está en uso por otra cuenta.')
            return redirect('settings')

        # --- Cambio de contraseña (opcional) ---
        password_changed = False
        if new_password:
            if not current_password:
                messages.error(request, 'Debes ingresar tu contraseña actual para cambiarla.')
                return redirect('settings')

            if not user.check_password(current_password):
                messages.error(request, 'La contraseña actual es incorrecta.')
                return redirect('settings')

            if len(new_password) < 8:
                messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
                return redirect('settings')

            user.set_password(new_password)
            password_changed = True

        # --- Guardar cambios ---
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Si cambió la contraseña, mantiene la sesión activa (sin esto, Django cerraría sesión)
        if password_changed:
            update_session_auth_hash(request, user)

        messages.success(request, 'Los cambios se guardaron correctamente.')
        return redirect('settings')

    return render(request, 'home/settings.html')