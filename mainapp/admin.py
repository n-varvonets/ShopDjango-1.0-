from django import forms  # need for 1st custom way
from django.forms import ModelChoiceField  # need for 2nd usual way
from django.forms import ModelForm, ValidationError  # need for creating own/custom form(for example for img NotebookAdminForm)
from django.contrib import admin
from PIL import Image  # to know the width and height of the image

from .models import *


class NotebookAdminForm(ModelForm):

    MIN_RESULUTION = (4000, 4000)

    def __init__(self, *args, **kwargs):  # method to be redefined/redirected_args in field
        super().__init__(*args, **kwargs)  # this is standard our form
        self.fields['image'].help_text = "Upload the image with minimal resolution {}x{}".format(
            *self.MIN_RESULUTION
        )  # in this form through our fields as a dict need to refer to our image for creating specify text(make custom)

    def clean_image(self):
        image = self.cleaned_data['image']  # save in a variable our picture, which is in the directory cleaned_data
        img = Image.open(image)  # use library to see width and height
        print(img.width, img.height)
        min_height, min_width = self.MIN_RESULUTION
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Image resolution less than minimum allowed!')
        return image


"""For our specific products it is necessary to limit bindings to categories in admin.py
when you create it, by the filter method. And there are two ways to do it. """


# 1st - create a class with custom logic in the first class and in the second you inherit this logic.
class NotebookCategoryChoiceField(forms.ModelChoiceField):
    pass


class NotebookAdmin(admin.ModelAdmin):

    form = NotebookAdminForm

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
