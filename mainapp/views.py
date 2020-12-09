from django.shortcuts import render
from django.contrib import messages  # for rendering request messages after some action under table of cart
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import Notebook, Smartphone, Powerbank, Category, LatestProducts, Cart, Customer, CartProduct
from .mixins import CategoryDetailMixin, CartMixin


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        # customer = Customer.objects.get(user=request.user)  # For DRY in the code we created in mixins CartMixin wh-->
        # cart = Cart.objects.get(owner=customer, in_order=False) # -->ich will give the user's cart(authorized and not)
        products = LatestProducts.objects.get_products_for_main_page(
            'notebook', 'smartphone', 'powerbank', with_respect_to='notebook'
        )  # with_respect_to - which product will be firs rendered on main page
        context = {
            'products': products,
            'categories': categories,
            'cart': self.cart
        }
        return render(request, "base.html", context)  # for ability to refer to a variable by name


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone,
        'powerbank': Powerbank
    }

    def dispatch(self, request, *args, **kwargs):  # is the entry point for requests (get,post...) and is eventually
        # responsible for returning the response we have already processed
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]  # refer to our dictionary CT_MODEL and pass it to
        # shop/urls as ct_model as the received key in self().
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    # model = Model  # in fact whole our model(one of notebook, smartphone, pw)
    # queryset = Model.objects.all()  # QuerySet is a list of objects of a given model
    context_object_name = 'product'  # how to refer in .html to our active product
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'  # for urlpatterns in url.py

    """get current name of category where we placed at the moment"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'


class AddCartToView(CartMixin, View):
    """get will be redirected on existing cart.html(not render own.html)"""

    def get(self, request, *args, **kwargs):
        # make print gotten kwargs in urls 'add-to-cart/<str:ct_model>/<str:slug>/' by clicking on button "add to cart"
        # print(kwargs.get('ct_model')) $ notebook - ct_model was taken from view.ProductDetailView
        # print(kwargs.get('slug')) $ nb_0002
        """There 3 steps for adding product to user's cart"""

        # 1) take all necessary data of active product/customer for creating content_product
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        # customer = Customer.objects.get(user=request.user)  # For DRY was created CartMixin
        # cart = Cart.objects.get(owner=customer, in_order=False) # For DRY was created CartMixin

        # 2) fill data in fields of models.CartProduct
        content_type = ContentType.objects.get(model=ct_model)  # define current model of category(object_pk)
        product = content_type.model_class().objects.get(slug=product_slug)  # model_class() - refer to parents class
        # print(product)  # Notebooks : Apple MacBook Pro 16" 1TB 2019 Space Gray

        # 3.1) Not check if product in cart. always create new one (create - take one object)
        # cart_product = CartProduct.objects.create(
        #     user=cart.owner, cart=cart, content_object=product, total_price=product.price)
        # was my fault by error (passed content_object=product) >>>ValueError: Cannot assign "<Notebook: Notebooks :
        # Apple MacBook Pro 16" 1TB 2019 Space Gray>": "CartProduct.content_type" must be a "ContentType" instance.

        # 3.2) First Check if product un cart - get. else: create new one (get_or_create take tuple(few objects))
        cart_product, created = CartProduct.objects.get_or_create(  # Unpack tuple | check created/not | true/false
            user=self.cart.owner, cart=self.cart, content_type=content_type,  object_id=product.id, total_price=product.price
        )  # to avoid the error "Field 'content_object' does not generate an automatic reverse relation and therefore
        # cannot be used for reverse querying. If it is a GenericForeignKey, consider adding a GenericRelation". -
        # - because content_object=product is missing from every copper product. But content_object can be defined
        # through the existing content_type and object_id in the product models.
        if created:
            self.cart.products.add(cart_product)
        self.cart.save()  # when we add some product our common cart of user save it changes
        messages.add_message(request, messages.INFO, 'Product successfully added')
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()  # delete object of cart_product from base (/admin/)
        self.cart.save()  # when we add some product our common cart of user save it changes
        messages.add_message(request, messages.INFO, 'Product successfully deleted')
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        # print(request.POST)  # show body POST $ <QueryDict: {'csrfmiddlewaretoken': ['3T7b1LmCZWWQTTSWlYBDHf5jZMeKaZH
        # XFsijYIwgdpoHzV70bTi3eVYX4'], 'qty': ['2']}> | qty - because I named csrf_token in input(POST) cart.html
        # 1) take our cart_product(same like in DeleteFromCartView... just get, not check)
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        # 2)assign him the value that comes from form request body POST
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()  # logic had in models.CartProduct (self.total_price = self.qty * self.content_object.price)
        self.cart.save()  # for changing data in cart
        messages.add_message(request, messages.INFO, 'Quantity successfully changed')
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        # try:
        #     # customer = Customer.objects.get(user=request.user)   # For DRY was created CartMixin
        #     # cart = Cart.objects.get(owner=customer)   # For DRY was created CartMixin
        # except ObjectDoesNotExist:
        #     cart = None
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)
