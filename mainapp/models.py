from django.db import models
from PIL import Image
import sys  # for finding size img
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from io import BytesIO  # need for convert img in bytes
from django.core.files.uploadedfile import InMemoryUploadedFile  # allows find files uploaded through forms (img)
from django.urls import reverse  # need for building url dor our object in mainapp/templates/product_detail.html
from django.utils import timezone


User = get_user_model()  # Return the User model that is active in this project


def get_product_url(obj, viewname):  # 1arg - our product, 2arg- name of pattern which we pass in shop/urls.pattern,
    ct_model = obj.__class__._meta.model_name  # every obj had hidden attribute 'meta' through which can get model name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})  # 'ct_model' - name of category which we
    #  pass to shop/urls.pattern as regular expression


def get_models_for_count(*model_names):  # get all possible created models/categories
    """return counted q-ty of product in category"""
    return [models.Count(model_name) for model_name in model_names]


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):

        products = []  # variable for 1st case(*args)
        with_respect_to = kwargs.get('with_respect_to')  # variable for 2nd case which had data of **kwargs
        """1st case [we want to render the last 5 created products]- we get *arg(for example 'nebooks' and make sort 
        last of 5) """
        ct_models = ContentType.objects.filter(model__in=args)  # make request ContentType to our models and
        # filtering them which we get in our **args**
        for ct_model in ct_models:  # ct_model - this is a "slug" of created category
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]  # model_class() - make
            # request to them parents (for example 'notebooks'). _base_manager - something like to reference to objects
            products.extend(model_products)
            #  """ 2nd case [We want to make the product we want more preferable]
        #  (e.g. smartphones are more priority than notebooks) - we get **kwargs """
        if with_respect_to:  # check if we got **kwargs
            ct_model = ContentType.objects.filter(model=with_respect_to)  # rewrite the variable "slug'
            if ct_model.exists():  # checking  received 'slag'/data_of_category_name that we got in **kwargs are
                # actually existing in our model.py
                if with_respect_to in args:  # checking if '*args' had at least one **kwargs
                    # ('fridge', 'power_bank', with_respect_to='notebook' - for checking this case of error)
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
                    # sorted our products by key, which we get by contacting to name of meta attribute 'slug' category
        return products


class LatestProducts:
    objects = LatestProductsManager()


# STR to see  data of LatestProducts with:
# _____1 args received:
# python manage.py shell
# from mainapp.models import LatestProducts
# LatestProducts.objects.get_products_for_main_page('smartphone', 'notebook')
# _____2+ args received=> **kwargs:
# LatestProducts.objects.get_products_for_main_page('smartphone', 'notebook', 'powerbank', with_respect_to='powerbank')


class CategoryManager(models.Manager):

    CATEGORY_NAME_СOUNT_NAME = {
        'Notebooks': 'notebook__count',
        'Smartphones': 'smartphone__count',
        'PowerBanks': 'powerbank__count'
    }  # if we in get_categories_for_left_sidebar make print(qs) we will get a dict with
    # <QuerySet [{'id': 1, 'name': 'Notebooks', 'slug': 'notebooks', 'notebook__count': 3, 'smartphone__count': 0,
    # 'powerbank__count': 0}, ... , }]>, we can get counted category by 'notebook__count'

    def get_queryset(self):
        return super().get_queryset()  # return based query set

    def get_categories_for_left_sidebar(self):
        models_qty = get_models_for_count('notebook', 'smartphone', 'powerbank')
        """There are 2 ways how to get category"""
        # 1st
        # qs = self.get_queryset().annotate(*models_qty).values()  # request the result of a basic set of model query
        # and apply an annotation to it to enable calculation of products in the category
        # return [dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_СOUNT_NAME[c['name']]])for c in qs]
        # returned to the view file in variable(categories) a list of the name, slug and category__counted
        # 2nd
        qs = list(self.get_queryset().annotate(*models_qty))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_СOUNT_NAME[c.name]))
            for c in qs
        ]   # c - certain obj of category(one of 'name', 'slug', 'notebook__count, ...)
        # count=getattr(c, self.CATEGORY_NAME_СOUNT_NAME[c.name] --> count=c.notebook__count
        return data


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name of category")
    slug = models.SlugField(unique=True)  # instead unique id we put the product name in url for find him
    objects = CategoryManager()

    def __str__(self):  # return instead 'object' --> name (how it will be presented when we receive the objects)
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})  # returns us the url of the page by specifying
        # the page_name from your url.py and tell kwargs that as a regular expression find a slug of category


class Product(models.Model):
    MIN_RESOLUTION = (50, 80)
    MAX_RESOLUTION = (200, 200)
    MAX_SIZE_IMG = 3145728  # 3 Mb = 3145728 bytes

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

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise MinResolutionErrorException('Image resolution less than minimum allowed!')
        # 1st case - crop the image with fixed proportions
        # if img.height > max_height or img.width > max_width:
        #     """if more than we cut img"""
        #     new_img = img.convert('RGB')
        #     resized_new_image = new_img.resize((150, 150), Image.ANTIALIAS)
        #     filestream = BytesIO()  # a variable that will convert an image into a data stream (bytes)
        #     resized_new_image.save(filestream, "JPEG", quality=90)
        #     filestream.seek(0)  # Moving to the 0(first) byte from the beginning of the file.
        #     new_name_resized_img = '{}'.format(self.image.name)
        #     self.image = InMemoryUploadedFile(
        #         filestream, "ImageField", new_name_resized_img, 'jpeg/image', sys.getsizeof(filestream), None
        #     )  # need to pass in InMemoryUploadedFile 6 args (file, field_name, name, content_type, size, charset)
        # super().save(*args, **kwargs)

        # 2nd case - the height is fixed and the width is proportionally variable.
        if img.height > max_height:  # if it exceeds ONLY the width size, img-fluid will correct it.
            img = img.convert('RGB')
            reduced_height = 160
            ratio = (reduced_height / float(img.size[1]))
            w_size = int((float(img.size[0]) * float(ratio)))
            resized_new_image = img.resize((w_size, reduced_height), Image.ANTIALIAS)
            filestream = BytesIO()  # a variable that will convert an image into a data stream (bytes)
            resized_new_image.save(filestream, "JPEG", quality=90)
            filestream.seek(0)  # Moving to the 0(first) byte from the beginning of the file.
            new_name_resized_img = '{}'.format(self.image.name)
            self.image = InMemoryUploadedFile(
                filestream, "ImageField", new_name_resized_img, 'jpeg/image', sys.getsizeof(filestream), None
            )  # need to pass in InMemoryUploadedFile 6 args (file, field_name, name, content_type, size, charset)
        super().save(*args, **kwargs)


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name="Customer", on_delete=models.CASCADE)
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
        return "Product: {} (in cart)".format(self.content_object.tittle)

    def save(self, *args, **kwargs):
        self.total_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Owner', on_delete=models.CASCADE)  # null=True for_anonymous_user
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')  # many models connection
    total_product = models.PositiveIntegerField(default=0)  # netbook= 2, Iphone = 3, products = 2, total_prod = 5
    total_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Total price')
    """in_order - True sign (user has made a purchase, you can't touch the cart anymore). Automatic False value - available for changes.
    for_anonymous_user - unregistered user has a cart, but he will not be able to formalize it."""
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    # """for calculating the quantity of products and their amount in the cart
    #  with the help of M2M by addressing to all products in the cart."""

    # def save(self, *args, **kwargs):
    #     cart_data = self.products.aggregate(models.Sum('total_price'), models.Count('id'))  # refer to all products
    #     # in cart, collect them and sum up the values by the total_price and id fields
    #
    #     # print(cart_data)  # {'total_price__sum': None, 'id__count': 0} - None can get error (need value) so make IF
    #     if cart_data.get('total_price__sum'):
    #         self.total_price = cart_data['total_price__sum']
    #     else:
    #         self.total_price = 0
    #     self.total_product = cart_data['id__count']  # not checking on None, because we get certain int value
    #     super().save(*args, **kwargs)  # the save method will be called in AddCartToView because I want to
    #     # refresh/resave data in cart ONLY when some product added to cart
    #
    # """but in the end project I understand that this logic doesn't work as need, because after created completed cart
    # status of cart in_order rewrite on True and django can't recognize the new cart in self., so for fix that need:
    # 1)to create utils.py; 2)copy-paste the logic of save() there; 3)delete this method from models.py"""


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_types = models.CharField(max_length=255, verbose_name='Display type')
    processor_freq = models.CharField(max_length=255, verbose_name='Processor frequency')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    video = models.CharField(max_length=255, verbose_name='Video card')
    time_without_charge = models.CharField(max_length=255, verbose_name='Time without charge')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.tittle)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')  # self - obj, 'product_detail' - created viewname


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

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


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

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Customer(models.Model):
    """connect user from settings.AUTH_MODEL"""

    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Number of phone', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Address', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Customer orders', related_name='related_customer')

    def __str__(self):
        return 'Customer: {} {}'.format(self.user.first_name, self.user.last_name)


"""STR adding products in python manage.py shell(be attentive, rename some variable and made migration and possible 
 inaccuracies of product-->products, user=customer )"""
# from mainapp.models import Notebook, CartProduct, Cart, Customer
# from django.contrib.auth import get_user_model
# User = get_user_model()
# u = User.objects.first()
# customer = Customer.objects.create(user=u, phone='12345', address='Baker street')
# notebook = Notebook.objects.first()
# c = Cart.objects.create(owner=customer, total_price=0)
# c.in_order $ False
# c.for_anonymous_user $ False
# cp = CartProduct.objects.create(content_object=notebook, user=customer, cart=c, total_price=notebook.price)
# cp <CartProduct: Product: HP Pavilion Mineral Silver (in cart)>
# c.products.add(cp)
# c.products.all()


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_OUR_STORES = 'our_stores'
    BUYING_TYPE_BY_COURIER_NP = 'courier_np'
    BUYING_TYPE_BY_SELF_NP = 'self_new_post'
    BUYING_TYPE_BY_SELF_UKR_POST = 'self_new_ukr_post'

    STATUS_CHOICE = (
        (STATUS_NEW, 'new_order'),
        (STATUS_IN_PROGRESS, 'order_in_process'),
        (STATUS_READY, 'order_is_ready'),
        (STATUS_COMPLETED, 'order_completed')
    )

    BUYING_CHOICE = (
        (BUYING_TYPE_OUR_STORES, 'From our stores '),
        (BUYING_TYPE_BY_COURIER_NP, 'By courier of NP to your address'),
        (BUYING_TYPE_BY_SELF_NP, 'By New Post Office'),
        (BUYING_TYPE_BY_SELF_UKR_POST, 'By UkrPost Office')
    )

    customer = models.ForeignKey(Customer, verbose_name='Customer', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='First name')
    last_name = models.CharField(max_length=255, verbose_name='Last name')
    phone = models.CharField(max_length=20, verbose_name='Number of phone')
    cart = models.ForeignKey(Cart, verbose_name='Cart', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Address', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Order status',
        choices=STATUS_CHOICE,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Order status',
        choices=BUYING_CHOICE,
        default=BUYING_TYPE_OUR_STORES
    )
    created_at = models.DateTimeField(auto_now=True, verbose_name='Date of created order')
    order_date = models.DateField(verbose_name='Order pickup date', default=timezone.now)
    comment = models.TextField(verbose_name='Comment to order', null=True, blank=True)

    def __str__(self):
        return str(self.id)
