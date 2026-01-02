from django.db import models

from django.db import migrations


class Category(models.Model):
    name_cat = models.CharField(max_length=100)

    def __str__(self):
        return self.name_cat
'''
ДЕЛАЛ по ПРИМЕРУ - пункт 106:
https://stackoverflow.com/questions/26927705/django-migration-error-you-cannot-alter-to-or-from-m2m-fields-or-add-or-remove
СДЕЛАЛ сам (с ПОЯСНЕНИЯМИпо этому ПРИМЕРУ - см. djangoM2MTest:
https://github.com/SergLavrov/djangoM2MTest/blob/master/persons/models.py
'''
'''
# null=True - допустимое значение NULL для поля в БАЗЕ ДАННЫХ!
# blank=True - поле может быть пустым в ФОРМАХ для ввода!
# unique=True - поле должно быть уникальным !
NULL - это специальное значение, которое используется в SQL для обозначения отсутствия данных. 
Оно отличается от пустой строки или нулевого значения, так как NULL означает отсутствие 
какого-либо значения в ячейке таблицы.

Разница между null=True и blank=True: https://sky.pro/media/raznicza-mezhdu-nulltrue-i-blanktrue-v-django/
-----null=True
Параметр null=True говорит о том, что в базе данных для данного поля может быть сохранено 
значение NULL. Это означает, что поле может не иметь значения. Этот параметр относится 
непосредственно к базе данных.

-----blank=True
Параметр blank=True говорит о том, что поле может быть пустым в формах. 
Это относится к валидации данных на уровне Django, а не базы данных. Если blank=False, 
то Django проверит, что поле не пустое, прежде чем сохранить значение в базу данных.
'''


class Size(models.Model):
    name_size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.name_size)

'''
Модели Product и Size остаются связанными отношением многие-ко-многим, 
однако теперь мы явно определяем промежуточную модель - 'ProductSize', 
которая связана отношением один-ко-многим с обеими моделями и при этом также определяет 
2 дополнительных поля. Для связи с промежуточной моделью в конструктор ForeignKey 
передается параметр "through", который указывает на название промежуточной таблицы, 
создаваемой для промежуточной модели 'ProductSize'.
'''


class Product(models.Model):
    name_prod = models.CharField(max_length=50)
    article = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    sizes = models.ManyToManyField(Size, through='ProductSize')
    # sizes = models.ManyToManyField(Size)

    def __str__(self):
        return self.name_prod

    def first_image(self):
        # из related_name = 'product_images' из class ProductImage(models.Model):
        return self.product_images.first()


'''
создание ДОПОЛНИТЕЛЬНЫХ полей в ПРОМЕЖУТОЧНОЙ  таблице ProductSize:
'''
class ProductSize(models.Model):
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size_in_stock = models.PositiveIntegerField(default=0)
    size_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.product} - {self.size}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField('/product_image/')

'''
Для M2M полей:
'''
def create_through_relations(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    ProductSize = apps.get_model('products', 'ProductSize')
    for prod in Product.objects.all():
        for size in prod.sizes.all():
            ProductSize(            # берем 4 поля из clas ProductSize
                size=size,
                product=prod,
                size_in_stock=0,
                size_price=0
            ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_create_models'),
    ]

    operations = [
        migrations.RunPython(create_through_relations, reverse_code=migrations.RunPython.noop),
    ]
