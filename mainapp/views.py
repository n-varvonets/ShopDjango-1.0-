from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import Notebook, Smartphone, Powerbank, Category, LatestProducts, Cart, Customer, CartProduct
from .mixins import CategoryDetailMixin


class BaseView(View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page(
            'notebook', 'smartphone', 'powerbank', with_respect_to='notebook'
        )  # with_respect_to - which product will be firs rendered on main page
        context = {
            'products': products,
            'categories': categories
        }
        return render(request, "base.html", context)  # for ability to refer to a variable by name


class ProductDetailView(CategoryDetailMixin, DetailView):
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


class CategoryDetailView(CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'


class AddCartToView(View):
    """get will be redirected on existing cart.html(not render own.html)"""

    def get(self, request, *args, **kwargs):
        # make print gotten kwargs in urls 'add-to-cart/<str:ct_model>/<str:slug>/' by clicking on button "add to cart"
        # print(kwargs.get('ct_model')) $ notebook - ct_model was taken from view.ProductDetailView
        # print(kwargs.get('slug')) $ nb_0002
        """There 3 steps for adding product to user's cart"""
        # 1) take all necessary data of active product/customer for creating content_product
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        customer = Customer.objects.get(user=request.user)
        # 2) fill data in fields of models.CartProduct
        cart = Cart.objects.get(owner=customer, in_order=False)
        content_type = ContentType.objects.get(model=ct_model)  # define current model of category(object_pk)
        product = content_type.model_class().objects.get(slug=product_slug)  # model_class() - refer to parents class
        # print(product)  # Notebooks : Apple MacBook Pro 16" 1TB 2019 Space Gray
        # 3) create and add new cart_product to the user's cart
        cart_product = CartProduct.objects.create(
            user=cart.owner, cart=cart, content_object=product, total_price=product.price  # total_price by default 1 qty
        )  # was my fault by error (passed content_object=product) >>>ValueError: Cannot assign "<Notebook: Notebooks :
        # Apple MacBook Pro 16" 1TB 2019 Space Gray>": "CartProduct.content_type" must be a "ContentType" instance.

        cart.products.add(cart_product)
        return HttpResponseRedirect('/cart/')


class CartView(View):

    def get(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=request.user)
            cart = Cart.objects.get(owner=customer)
        except ObjectDoesNotExist:
            cart = None
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'cart': cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)
