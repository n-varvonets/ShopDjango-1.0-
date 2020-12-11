from django.db import models


def recalc_cart(cart):  # function explanation u can see in models.py.Cart
    cart_data = cart.products.aggregate(models.Sum('total_price'), models.Count('id'))
    if cart_data.get('total_price__sum'):
        cart.total_price = cart_data['total_price__sum']
    else:
        cart.total_price = 0
    cart.total_product = cart_data['id__count']
    cart.save()
