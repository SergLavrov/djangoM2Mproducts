from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
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


    # ПРИМЕР:
    # class Product(models.Model):
    #     name = models.CharField(max_length=255)
    #
    # class ProductImage(models.Model):
    #     product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    #     image = models.ImageField(upload_to='product_images/')
    #     created_at = models.DateTimeField(auto_now_add=True)
    #
    # products_with_first_image = []
    #
    # for product in Product.objects.prefetch_related('images'):
    #     first_image = product.images.first()
    #     products_with_first_image.append({
    #         'product': product,
    #         'image': first_image.image.url if first_image else None
    #     })
    #
    # { %  for item in products_with_first_image %}
    #   < div class ="product" >
    #     < h2 > {{item.product.name}} < / h2 >
    #     { % if item.image %}
    #         < img src = "{{ item.image }}" alt = "{{ item.product.name }}" >
    #     { % else %}
    #         < p > Нет изображения < / p >
    #     { % endif %}
    #   < / div >
    # { % endfor %}


def add_product(request):
    if request.method == 'POST':
        name_prod = request.POST.get('name_prod')    # name="name_prod" из шаблона add_product.html
        article = request.POST.get('article')           # name="article"
        category_id = request.POST.get('category_id')   # name="category_id"

        # 1 Вар для ManyToManyField (для выбора ОДНОГО размера):
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
