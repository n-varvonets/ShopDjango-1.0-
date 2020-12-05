from django.shortcuts import render
from django.views.generic import DetailView
from .models import Notebook, Smartphone, Powerbank, Category


def test_view(request):
    categories = Category.objects.get_categories_for_left_sidebar()
    return render(request, "base.html", {'categories': categories})  # for ability to refer to a variable by name


class ProductDetailView(DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone' : Smartphone,
        'power_bank' : Powerbank
    }
    def dispatch(self, request, *args, **kwargs): # is the entry point for requests (get,post...) and is eventually
    # responsible for returning the response we have already processed
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]  # refer to our dictionary CT_MODEL and pass it to
    # shop/urls as ct_model as the received key in self().
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    # model = Model  # in fact whole our model(notebook, smartphone, pw)
    # queryset = Model.objects.all()  # QuerySet is a list of objects of a given model
    context_object_name = 'product'  # 'product' - because it will be common to us.
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'