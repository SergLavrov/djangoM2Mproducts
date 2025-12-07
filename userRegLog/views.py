from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

# from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

from .forms import UserAddFieldForm  # импортируем нашу "кастомную форму" для регистрации из forms.py

# class MainView(TemplateView):
#     template_name = 'products/home.html'
#     def get(self, request):
#         return render(request, 'products/home.html')


# Вариант 1.2 - когда добавлено поле email в UserAddFieldForm из (forms.py)
class RegisterFormView(FormView):
    # RegisterFormView унаследован от класса FormView, который импортируем из django.views.generic.edit !!!

    # form_class = UserCreationForm  # Элементарная форма для регистрации!

    form_class = UserAddFieldForm  # Используем нашу "кастомную форму" для регистраци из forms.py

    template_name = 'userRegLog/register.html'

    # success_url = 'login'

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('login')   # При успешной регистрации перенаправляем на страницу "ВХОДА"!

    def form_invalid(self, form):
        return super(RegisterFormView, self).form_invalid(form)


# Вариант 1.1 - стандартная регистрация пользователя: username, password1, password2
# class RegisterFormView(FormView):
#     # 1.RegisterFormView унаследован от класса FormView, который импортируем из django.views.generic.edit !!!
#
#     form_class = UserCreationForm  # Элементарная форма для регистрации!
#     '''
#     1. Имортируем его - from django.contrib.auth.forms import UserCreationForm
#     2. UserCreationForm - это стандартный класс для создания форм, который представляет Django из своей "КОРОБКИ"
#     для стандартной ВАЛИДАЦИИ вводимых данных:
#     - Обязательное поле.Не более 150 символов.Только буквы, цифры и символы @ /./ + / - / _.
#     - Пароль не должен быть слишком похож на другую вашу личную информацию.
#     - Ваш пароль должен содержать как минимум 8 символов.
#     - Пароль не должен быть слишком простым и распространенным.
#     - Пароль не может состоять только из цифр.
#     - Ошибка: Пользователь с таким именем уже существует.
#     - Ошибка: Введенный пароль слишком похож на имя пользователя.
#     - Подтверждение пароля: Ошибка - Пароли не совпадают.
#     - Подтверждение пароля: Ошибка - Для подтверждения введите, пожалуйста, пароль ещё раз.
#     '''
#
#     template_name = 'userRegLog/register.html'
#
#     # success_url = 'login'
#
#     def form_valid(self, form):
#         form.save()
#         return super(RegisterFormView, self).form_valid(form)
#
#     def get_success_url(self):
#         return reverse('login')   # При успешной регистрации перенаправляем на страницу "ВХОДА"!
#
#     def form_invalid(self, form):
#         return super(RegisterFormView, self).form_invalid(form)


class LoginFormView(FormView):

    form_class = AuthenticationForm
    '''
    1. Импортируем его - from django.contrib.auth.forms import AuthenticationForm
    2.from django.contrib.auth import login
    Ощибка: Пожалуйста, введите правильные имя пользователя и пароль. Оба поля могут быть чувствительны к регистру.
    '''

    template_name = 'userRegLog/login.html'

    success_url = '/products/get-products/'

    def form_valid(self, form):
        # Получаем пользователя на основе введенных в форму данных и авторизуем его!
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

    # def form_invalid(self, form):
    #     return super(LoginFormView, self).form_invalid(form)


class LogoutView(View):
    # унаследован от класса View
    # импортируем View - from django.views import View
    # from django.contrib.auth import logout

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('get-products')) # Выходим на главную страницу!
