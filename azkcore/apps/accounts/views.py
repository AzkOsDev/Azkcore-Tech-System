from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# VIEW LOGIN USERS
def login(request):
    # Si el usuario ya inició sesión, lo mandamos directo al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # desde una vista protegida con @login_required
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales Incorrectas. Por favor, inténtalo de nuevo.')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')

@login_required
def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    return redirect('login')
