from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm


class UserAddFieldForm(UserCreationForm): # наследуемся / импортируем - import UserCreationForm (см. в файле views.py)
    email = forms.EmailField(required=True)   #required - значит поле обязательно для заполнения!
                                       # если на сайте НЕ заполнить это поле, то выведится сообщение - "Заполните поле"
    # first_name = forms.CharField(label="Имя")
    # last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User  # импортируем - import User из коробки Django
        fields = ("username", "email", "password1", "password2")

    # Проверка на email со стороны браузера :
    # - example (... отсутствует символ @)
    # - example@ (Введите часть адреса после символа @. Адрес ... неполный!)

    # Проверка на email со стороны django:
    # - example@gmail (Введите правильный адрес электронной почты.)

    def clean_email(self):                     # Проверка на email также со стороны сервера:
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email уже существует!")
        return email

    def save(self, commit=True):
        user = super(UserAddFieldForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]   # добавляем email
        if commit:
            user.save()
        return user

    # Пояснение - в этой функции мы переопределяем стандартный метод "save",
    # (из views.py -> def form_valid(self, form) --> form.save() --> здесь для него ставим: save(commit=False));
    # получаем из cleaned_data["email"] и сохраняем пользователя в базу данных, но уже с email !!!
    # И возвращаем его --> return user.


# Справочно: Чтобы не усложнять Регистрацию, оставим поля username, email, password1, password2.
# Oстальные поля можно вынести в Profile (см. пример в приложении ProfileModalClothShop)
#
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     age = models.IntegerField(null=True)
#     phone = models.CharField(max_length=20, unique=True)
#     postcode = models.CharField(max_length=6)
#     about = models.TextField(blank=True)
#     time_created = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField('/my_avatar/')

# + class ProfileForm(forms.Form): !!! из forms.py !!!