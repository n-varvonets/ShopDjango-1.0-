from django import forms
from django.contrib import admin

from .models import *


class NotebookCategoryChoiceField(forms.ModelChoiceField):
    """when creating a new product, it is necessary to assign it a category, to filter out unnecessary ones and by this
    not to allow choosing the wrong product category """
    pass


class NotebookAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """If a table/model in DB is called a category, then we filter all our tables/models from models by slug our
        criterion when creating a table/model """
        if db_field.name == 'category':
            return NotebookCategoryChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)  # if not,we get a standard operating model


class SmartphoneCategoryChoiceField(forms.ModelChoiceField):
    pass


class SmartphoneAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return SmartphoneCategoryChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PowerbankCategoryChoiceField(forms.ModelChoiceField):
    pass


class PowerbankAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return PowerbankCategoryChoiceField(Category.objects.filter(slug='powerbanks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(CartProduct)
admin.site.register(Notebook, NotebookAdmin)  # NotebookAdmin for filter when creating new product
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(Powerbank, PowerbankAdmin)
admin.site.register(Cart)
admin.site.register(Customer)
