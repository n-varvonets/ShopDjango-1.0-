from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import Category, Cart, Customer


class CategoryDetailMixin(SingleObjectMixin):
    """get current name of category where we placed at the moment"""
    def get_context_data(self, **kwargs):
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


