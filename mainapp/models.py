from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()  # we tell django what want use user what specify in settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name of category")
    slug = models.SlugField(unique=True)  # instead unique id we put the product name in url for find him

    def __str__(self):  # return instead 'object' --> name(как он у нас будет представлен, когда будем получать обьекты)
        return self.name


class Product(models.Model):
    """Make abstract model(without migrations with DB, just for inheritance)"""

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)  # connect by model
    # Category and in case delete - we delete  all connections
    tittle = models.CharField(max_length=255, verbose_name='Product name')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Image")
    description = models.TextField(verbose_name="Description", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Price')

    def __str__(self):
        return self.tittle


class CartProduct(models.Model):
    customer = models.ForeignKey('Customer', verbose_name="Customer", on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE)
    """In order not to create n quantity of new Class(Products) in the cart, we create it as a single external 
    Class(Product) and then with the use of these 3 lines we inherit its characteristics, passing the name of 
    Class(Product) to ContentType. """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    qty = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return "Product: {} (in cart)".format(self.product.tittle)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_types = models.CharField(max_length=255, verbose_name='Display type')
    processor_freq = models.CharField(max_length=255, verbose_name='Processor frequency')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    video = models.CharField(max_length=255, verbose_name='Video card')
    time_without_charge = models.CharField(max_length=255, verbose_name='Time without charge')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.tittle)


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_types = models.CharField(max_length=255, verbose_name='Display type')
    resolution = models.CharField(max_length=255, verbose_name='Display resolution')  # 720x480
    accum_volume = models.CharField(max_length=255, verbose_name='Battery volume')
    sd = models.BooleanField(default=True)  # bool value, because most phones have an sd card
    main_camera_mp = models.CharField(max_length=255, verbose_name=' Main camera')
    frontal_camera_mp = models.CharField(max_length=255, verbose_name=' Frontal camera')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.tittle)


class Powerbank(Product):
    voltage = models.CharField(max_length=255, verbose_name='Voltage')
    ampere_flow = models.CharField(max_length=255, verbose_name='Ampere Flow')
    Fast_charging = models.BooleanField(default=True)
    wireless = models.BooleanField(default=True)
    capacity = models.CharField(max_length=255, verbose_name='Capacity')
    size = models.CharField(max_length=255, verbose_name='Size')
    weight = models.CharField(max_length=255, verbose_name='Weight')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.tittle)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Owner', on_delete=models.CASCADE)
    product = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')  # many models connection
    total_product = models.PositiveIntegerField(default=0)  # netbook= 2, Iphone = 3, products = 2, total_prod = 5
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    """connect user from settings.AUTH_MODEL"""

    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Number of phone')
    address = models.CharField(max_length=255, verbose_name='Address')

    def __str__(self):
        return 'Customer: {} {}'.format(self.user.first_name, self.user.last_name)
