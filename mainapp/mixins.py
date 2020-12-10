from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import Category, Cart, Customer, Notebook, Smartphone, Powerbank


class CategoryDetailMixin(SingleObjectMixin):

    CATEGORY_MODEL2PRODUCT_MODEL = {
        "notebooks": Notebook,
        'smartphones': Smartphone,
        'powerbanks': Powerbank
    }

    def get_context_data(self, **kwargs):
        """need to render our product by the categories"""
        if isinstance(self.get_object(), Category):  # need to take get_object ONLY for categories(not for products)
            model = self.CATEGORY_MODEL2PRODUCT_MODEL[self.get_object().slug]  # get one of models by received slug
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()
            context['category_products'] = model.objects.all()  # all data of product by key for cart.html. Output:
            # Smartphones <QuerySet [<Smartphone: Smartphones : Apple iPhone 12 128GB Black>,
            # <Smartphone: Smartphones : Samsung Galaxy S20 Plus 8/128GB Cosmic Gray>]>
            return context
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categories_for_left_sidebar()
        return context


class CartMixin(View): # view - because he has def dispatch
    """for DRY(fields of cart and customer in diff classes)  in views"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # if our user passed authenticated and we now him
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:  # extra check before I create the user authentication ability (i.e. mandatory
                # synchronization with the customer) after created the func this condition will be changed

                customer = Customer.objects.create(
                    user=request.user  # only 1 external key, because phone/address is nullable in models.py
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:  # if cart not found - we have to create her
                cart = Cart.objects.create(owner=customer)

        else:  # for not authenticated users
            cart = Cart.objects.filter(for_anonymous_user=True)  # if we find cart for anonymous user
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)


