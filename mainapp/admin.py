from django import forms  # need for 1st custom way
from django.forms import ModelChoiceField  # need for 2nd usual way
from django.contrib import admin

from .models import *

"""For our specific products it is necessary to limit bindings to categories in admin.py
when you create it, by the filter method. And there are two ways to do it. """


# 1st - create a class with custom logic in the first class and in the second you inherit this logic.
class NotebookCategoryChoiceField(forms.ModelChoiceField):
    pass


class NotebookAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # If a table/model in DB is called a category,
        # then we filter all our tables/models from models by slug our criterion when creating a table/model
        if db_field.name == 'category':
            return NotebookCategoryChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)  # if not,we get a standard operating model


# 2nd - without custom logic (using only one class), directly inheriting ModelChoiceField.
class SmartphoneAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))  # just put ModelChoiceField instead
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PowerbankAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='powerbanks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(CartProduct)
admin.site.register(Notebook, NotebookAdmin)  # NotebookAdmin for filter when creating new product
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(Powerbank, PowerbankAdmin)
admin.site.register(Cart)
admin.site.register(Customer)
