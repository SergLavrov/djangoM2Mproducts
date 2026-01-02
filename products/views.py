from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ValidationError
from products.models import Product, Category, Size, ProductSize, ProductImage

# def home(request):
#     return render(request, 'products/home.html')


# def create_through_relations(apps, schema_editor):
#     Product = apps.get_model('products', 'Product')
#     ProductSize = apps.get_model('products', 'ProductSize')
#     for prod in Product.objects.all():
#         for size in prod.sizes.all():
#             ProductSize(  # берем 4 поля из clas ProductSize
#                 size=size,
#                 product=prod,
#                 size_in_stock=0,
#                 size_price=0
#             ).save()

def get_prods(request):
    category_list = Category.objects.all()
    products = Product.objects.all().filter(is_deleted=False)

    data = {
        'categories': category_list,
        'products': products,
    }
    return render(request, 'products/all_products.html', data)


def add_product3(request):
    """
        Представление для добавления нового товара.
        Обрабатывает как GET, так и POST запросы.
        Для GET запросов извлекает список категорий и типов товаров и рендерит шаблон 'add_product.html' с данными.
        Для POST запросов извлекает детали товара из запроса и сохраняет новый товар в БД,
        затем перенаправляется на URL 'get-products'.
    """
    if request.method == 'POST':                        # если запрос POST, сохраняем данные
        name_prod = request.POST.get('name_prod')       # name="name_prod" из шаблона add_product.html
        article = request.POST.get('article')           # name="article"
        category_id = request.POST.get('category_id')   # name="category_id"
        # выбранные размеры из чекбокса через getlist
        size_ids = request.POST.getlist('sizes_for_getlist')  # name="sizes_for_getlist" из шаблона add_product3.html

        try:
            if not name_prod or not article or not category_id:
                raise ValidationError('Заполните все обязательные поля!')

            if not size_ids:
                raise ValidationError('Выберите хотя бы один размер товара на складе!')

            name_prod = str(name_prod)
            if not name_prod.isalpha():  # возвращает True, если все символы в строке являются буквами!
                raise ValidationError('Название должно содержать только буквы!')

            category = Category.objects.get(id=category_id)

        # ДОПОЛНИТЕЛЬНЫЕ поля из ПРОМЕЖУТОЧНОЙ  таблицы "ProductSize":
        # Т.к. формируются несколько значений для одного и того же ключа - size_in_stock и size_price - используем getlist!!
        # Для ПОСЛЕДНЕГО РАБОЧЕГО ВАРИАНТА НЕ понадобился getlist!!!

            # size_in_stock_list = request.POST.getlist('size_in_stock')
            # size_price_list = request.POST.getlist('size_price')

            product = Product.objects.create(              # Создаем НОВЫЙ объект Product и сохраняем его в БД
                name_prod=name_prod,
                article=article,
                category=category,
                is_deleted=False,
            )
            # product.save()

            ''' 
            СПРАВОЧНО: В Django есть 2 варианта сохранения объекта в БД.
            # а) Т.к мы  используем именно .objects.create(...), объект сразу сохраняется в базе!!!
            # Вызов save() НЕ нужен — метод .create() внутри себя делает obj = Model(...); obj.save().
            #
            # б) Через конструктор .save()
            # product = Product(
            #     name_prod=name_prod,
            #     article=article,
            # )
            # product.save()
            '''

            # Связываем размеры
            # ПОСЛЕДНИЙ РАБОЧИЙ ВАРИАНТ - каждый выбранный размер связывался со своим "количеством" и "ценой".
            # Теперь всё работает по "size_id" !!!
            # см. также в шаблоне: name="size_in_stock_{{ size.id }}" и name="size_price_{{ size.id }}"
            for size_id in size_ids:
                size = Size.objects.get(id=size_id)

                raw_stock = request.POST.get(f'size_in_stock_{size_id}', '').strip()
                raw_price = request.POST.get(f'size_price_{size_id}', '').strip()
                '''
                    P.S.функция .strip() полезна, когда нужно "очистить" строку от пробелов, лишних символов или 
                    спецзнаков по краям!!! Пользователь может случайно ввести пробелы в начале/конце: " 25 " и т.д.
                    .strip() убирает эти пробелы в начале и в конце строки, чтобы дальше можно было корректно преобразовать
                    строку в число(int, Decimal) или сохранить в базе без лишних пробелов !!!
                '''

                # Проверка обязательности
                if not raw_stock or not raw_price:
                    raise ValidationError(f'Для размера {size.name_size} заполните количество товара и цену!')

                stock = int(raw_stock) if raw_stock.isdigit() else 0
                # допускаем десятичные цены, заменяем запятую на точку
                raw_price = raw_price.replace(',', '.')
                try:
                    price = float(raw_price) if raw_price else 0.0
                except ValueError:
                    price = 0.0

            # ДОПОЛНИТЕЛЬНЫЕ поля в ПРОМЕЖУТОЧНОЙ  таблице "ProductSize":
                ProductSize.objects.create(
                    product=product,
                    size=size,
                    size_in_stock=stock,
                    size_price=price,
                )
                # prodsize.save()

            # Фото
            images = request.FILES.getlist('images_for_getlist')  # name="images_for_getlist" из шаблона add_product.html
            # Проверка обязательности загрузки фото
            if not images:
                raise ValidationError('Загрузите хотя бы одно фото товара!')

            # if len(images) < 2:
            #     raise ValidationError('Загрузите минимум 2 фото товара!')

            for image in images:
                ProductImage.objects.create(product=product, image=image)  # create-сохраняем в БД

            return HttpResponseRedirect(reverse('get-products'))

        except ValidationError as e:
            error = str(e)

            category_list = Category.objects.all()
            size_list = Size.objects.all()
            data = {
                'categories': category_list,
                'size_list': size_list,
                'error': error,
            }

            return render(request, 'products/add_product3.html', data)

    else:
        category_list = Category.objects.all()
        size_list = Size.objects.all()
        data = {
            'categories': category_list,
            'size_list': size_list,
        }

        return render(request, 'products/add_product3.html', data)



def add_product2(request):
    if request.method == 'POST':
        name_prod = request.POST.get('name_prod')       # name="name_prod" из шаблона add_product.html
        article = request.POST.get('article')           # name="article"
        category_id = request.POST.get('category_id')   # name="category_id"

        # 1 Вар для ManyToManyField (для выбора ОДНОГО размера через SELECT):
        size_id = request.POST.get('size_id')  # name='size_id' Получаем id "выбранного размера" из POST-запроса!

        # ДОПОЛНИТЕЛЬНЫЕ поля в ПРОМЕЖУТОЧНОЙ  таблице "ProductSize":
        size_in_stock = request.POST.get('size_in_stock')  # name="size_in_stock"
        size_price = request.POST.get('size_price')  # name="size_price"

        category = Category.objects.get(id=category_id)

        # 1 Вар для ManyToManyField (для выбора ОДНОГО размера):
        size = Size.objects.get(id=size_id)  # Получаем по id "нужный размер" в БД!

        product = Product.objects.create(
            name_prod=name_prod,
            article=article,
            category=category,
        )
        product.save()

        # НЕ Делаем ! Т.к в этом случае в таблицу "products_productssize" добавляется один товар ДВАЖДЫ !!! :
        # Первый раз БЕЗ заполнения полей "size_in_stock" и "size_price", Второй раз с заполнением !!!
        # СВЯЗЫВАЕМ Продукт и Размер: "sizes" - это поле из class Product (sizes = models.ManyToManyField(Size))
        # 1 Вар: - если добавляем один размер используем метод "add":
        # product.sizes.add(size) или product.sizes.set([size])


        # ДОПОЛНИТЕЛЬНЫЕ поля в ПРОМЕЖУТОЧНОЙ  таблице "ProductSize":
        prodsize = ProductSize(
            product=product,
            size=size,
            size_in_stock=size_in_stock,
            size_price=size_price,
        )
        prodsize.save()

        images = request.FILES.getlist('images_for_getlist') # name="images_for_getlist" из шаблона add_product.html
        for image in images:
            # img = ProductImage(product=product, image=image)
            img = ProductImage.objects.create(
                product=product,
                image=image,
            )
            img.save()

        return HttpResponseRedirect(reverse('get-products'))

    else:

        category_list = Category.objects.all()
        size_list = Size.objects.all()
        data = {
            'categories': category_list,
            'size_list': size_list,
        }

        # return render(request, 'products/add_product3.html', data)
        return render(request, 'products/add_prod2.html', data)

# СМОТРИ ПРИМЕР ВЫШЕ для ОДНОГО размера. УЛУЧШИЛ - переставил немного местами !!!
# def add_product(request):
#     if request.method == 'POST':
#         name_prod = request.POST.get('name_prod')    # name="name_prod" из шаблона add_product.html
#         article = request.POST.get('article')           # name="article"
#         category_id = request.POST.get('category_id')   # name="category_id"
#         # size_id = request.POST.get('size_id')  # name='size_id' Получаем id "выбранного размера" из POST-запроса!
#
#         # ПРОБОВАЛ:
#         size_in_stock = request.POST.get('size_in_stock')  # name="size_in_stock"
#         size_price = request.POST.get('size_price')
#
#         # 1 Вар для ManyToManyField (для выбора ОДНОГО размера):
#         # size_id = request.POST.get('size_id')  # name='size_id' Получаем id "выбранного размера" из POST-запроса!
#
#         # 2 Вар для ManyToManyField (для выбора НЕСКОЛЬКИХ размеров):
#         """ Используем getlist для получения всех выбранных значений из нашего чекбокса,
#             иначе при использовании get будет возвращено только последнее выбранное значение.
#         """
#         sizes_ids = request.POST.getlist('sizes_for_getlist')  # name="sizes_for_getlist"
#                                                               # Получаем id всех выбранных размеров из БД для checkbox:
#
#         category = Category.objects.get(id=category_id)
#
#         product = Product.objects.create(
#             name_prod=name_prod,
#             article=article,
#             category=category,
#         )
#         product.save()
#         # 1 Вар для ManyToManyField:
#         # size = Size.objects.get(id=size_id)  # Получаем по id "нужный размер" в БД!
#
#         # СВЯЗЫВАЕМ Продукт и Размер: "sizes" - это поле из class Product (sizes = models.ManyToManyField(Size))
#         # ПРИМЕР см. https: // metanit.com / python / django / 5.11.php
#
#         # 1 Вар: - если добавляем один размер:
#         # product.sizes.add(size)
#
#         # 2 Вар для ManyToManyField: - если привязывем ПРОДУКТУ с одним id НЕСКОЛЬКО размеров:
#         sizes_selected = Size.objects.filter(id__in=sizes_ids)
#         product.sizes.set(sizes_selected)
#
#         # ПРОБОВАЛ:
#         prodsize = ProductSize(
#             product=product,
#             size=sizes_selected,
#             size_in_stock=size_in_stock,
#             size_price=size_price,
#         )
#         prodsize.save()
#
#         images = request.FILES.getlist('images_for_getlist') # name="images_for_getlist" из шаблона add_product.html
#         for image in images:
#             # img = ProductImage(product=product, image=image)
#             img = ProductImage.objects.create(
#                 product=product,
#                 image=image,
#             )
#             img.save()
#
#         return HttpResponseRedirect(reverse('get-products'))
#
#     else:
#
#         category_list = Category.objects.all()
#         size_list = Size.objects.all()
#         data = {
#             'categories': category_list,
#             'sizes': size_list,
#         }
#
#         return render(request, 'products/add_product.html', data)


def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    '''
    Получили ВСЕ фото для данного продукта!
    [1:] - Кроме первого фото, т.к. ПЕРВОЕ ФОТО д.б. - active !!! Это обязательное условие для КАРУСЕЛИ !!!
    cм. шаблон product_detail.html!
    '''
    product_images = ProductImage.objects.filter(product=product)[1:]
    data = {
        'product': product,
        'product_images': product_images,
    }

    return render(request, 'products/product_detail.html', data)
