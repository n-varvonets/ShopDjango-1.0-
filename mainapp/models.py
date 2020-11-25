from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User = get_user_model()  # we tell django what want use user what specify in settings.AUTH_USER_MODEL

# Create your models here:
# 1 Category
# 2 Product
# 3 CartProduct(in basket)
# 4 Basket/Cart(Сама корзина)
# 5 Order
# *********
# 6 Customer
# 7 Specification of product(характеристики...там даиганаль, ёмкость батарее и т.д.)


class Category(models.Model):
    """То что в нашем url будет endpoint-ом конечным
    (куда мы хотим попасть, что бы получить какаой-то конкретный обьект модели)"""
    name = models.CharField(max_length=255, verbose_name="Name of category")
    slug = models.SlugField(unique=True)  # instead unique id we put the product name in url for find him

    def __str__(self):  # return instead 'object' --> name(как он у нас будет представлен, когда будем получать обьекты)
        return self.name


class Product(models.Model):

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
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE, related_name='related_product')
    qty = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return "Product: {} (in cart)".format(self.product.tittle)



class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Owner', on_delete=models.CASCADE)
    product = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')  # many models connection
    total_product = models.PositiveIntegerField(default=0)  # netbook= 2, Iphone = 3, products = 2, total_prod = 5
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    '''connect user from settings.AUTH_MODEL'''

    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Number of phone')
    address = models.CharField(max_length=255, verbose_name='Address')

    def __str__(self):
        return 'Customer: {} {}'.format(self.user.first_name, self.user.last_name)


class Specifications(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255, verbose_name='Name of product')

    def __str__(self):
        return 'Specifications for products {}'.format(self.name)
