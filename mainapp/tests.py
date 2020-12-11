from decimal import Decimal
from unittest import mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile  # for creating test img
from .models import Category, Notebook, CartProduct, Cart, Customer
from .views import recalc_cart, AddCartToView, BaseView


User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:  # special test django function
        self.user = User.objects.create(username='testuser', password='password')
        self.category = Category.objects.create(name='Notebooks', slug='notebooks')

        # image = SimpleUploadedFile(name="test.jpg", content=b'', content_type='image/jpg')  # it doesn't test
        # correctly because in code have limit on resolution, so upload static img from local dir
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('/home/nickolay/PycharmProjects/shop/shop/media/001_MwMNjEf.jpg', 'rb').read(),
            content_type='image/jpeg'
        )
        self.notebook = Notebook.objects.create(
            category=self.category,
            tittle='Test notebook',
            slug='test-slug',
            image=image,
            price=Decimal('999.99'),
            diagonal='17.3"',
            display_types='IPS',
            processor_freq='3,4 GHz',
            ram='6 GB',
            video='GeForce GTX 1080',
            time_without_charge='20 h'
        )
        self.customer = Customer.objects.create(user=self.user, phone='+38093999999', address='Test str.')
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.notebook
        )

    def test_add_to_cart(self):  # name of test should starts with prefix 'test_'
        # for correctly running 'python mange.py test' cmd

        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        """with created new cart_product make next test-cases:"""
        # 1)the object is in the cart
        self.assertIn(self.cart_product, self.cart.products.all())  # checks the occurrence of something in something
        # 2)the q-ty of objects in the cary is only 1 (no duplication)
        self.assertEqual(self.cart.products.count(), 1)
        # 3)business logic correctly count total price
        self.assertEqual(self.cart.total_price, Decimal('999.99'))

    def test_response_from_add_to_cart_view(self):
        """testing through views """
        factory = RequestFactory()
        request = factory.get('')  # necessary something to pass in request
        request.user = self.user
        response = AddCartToView.as_view()(request, ct_model='notebook', slug='test-slug')
        # need at AddCartToView to comment(#) messages for fix some err
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart/')

    def test_mock_homepage(self):
        mock_data = mock.Mock(status_code=444)  # create an instance with any attrs
        with mock.patch('mainapp.views.BaseView.get', return_value=mock_data) as mock_data_:  # emulate method get in models.py
            factory = RequestFactory()
            request = factory.get('')  # necessary something to pass in request
            request.user = self.user
            response = BaseView.as_view()(request)
            self.assertEqual(response.status_code, 444)  # although in fact the method GET should return 200




