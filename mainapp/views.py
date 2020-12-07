from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import Notebook, Smartphone, Powerbank, Category, LatestProducts, Cart, Customer
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
    context_object_name = 'product'  # 'product' - because it will be common to us.
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
        # make print what we get in urls 'add-to-cart/<str:ct_model>/<str:slug>/'
        print(kwargs.get('ct_model'))
        print(kwargs.get('slug'))

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



