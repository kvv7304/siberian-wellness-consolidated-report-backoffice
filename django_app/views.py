import datetime
import threading
from datetime import datetime

import requests
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from backoffice import table_main, backoffice, auth  # noqa
from django_app.forms import RegistrationForm, LoginForm


def load(request):
    if request.method == 'POST':
        user = request.user
        test = {'number': user.sw_numer, 'password': user.sw_password}
        error = auth(test)
        if isinstance(error, requests.sessions.Session):
            # Запускаем backoffice функцию в отдельном потоке
            thread = threading.Thread(target=backoffice, args=(user.sw_numer, user.sw_password, user.pk, user.first_name, request))
            thread.start()
            # Открываем страницу loading
            return render(request, 'loading.html')

        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            context = {
                'table_data': None,
                'name': error,
                'last_modified': current_time,
            }
            return render(request, 'main.html', context)

    return render(request, 'main.html')


class CustomLoginView(LoginView):
    template_name = 'registration.html'
    authentication_form = LoginForm


class CustomRegisterView(CreateView):
    template_name = 'registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    model = get_user_model()


class CustomFormView(FormView):
    template_name = 'registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('table_main')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)


def save(request):
    if request.method == 'POST':
        if 'fill_fields' in request.POST:
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.sw_numer = request.POST.get('sw_numer')
            user.sw_password = request.POST.get('sw_password')
            user.save()
            return load(request)
    return render(request, 'table_main.html', {'user': request.user})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('table_main')
    else:
        # Возможно, что-то делаете, если запрос не является POST
        return render(request, 'logout.html')

def check_process_status(request):
    if request.user.status:
        return JsonResponse({'status': 'completed'})
    else:
        return JsonResponse({'status': 'in_progress'})
