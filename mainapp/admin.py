from django import forms  # need for 1st custom way
from django.forms import ModelChoiceField  # need for 2nd usual way
from django.forms import ModelForm, ValidationError  # need for creating own/custom form
from django.contrib import admin
from django.utils.safestring import mark_safe  # need for making colorful text


from .models import *


class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):  # method to be redefined/redirected_args in field
        super().__init__(*args, **kwargs)  # this is standard our form
        self.fields['image'].help_text = mark_safe("""<span style='color:red'>Upload the image have to be with minimal
         resolution {}x{}</span><br><span style='color:red'>Upload the image more than maximum available resolution
          {}x{} will be cropped.</span>""".format(*Product.MIN_RESOLUTION, *Product.MAX_RESOLUTION))

    def clean_image(self):  # for form in /admin
        image = self.cleaned_data['image']  # save in a variable our picture, which is in the directory cleaned_data
        img = Image.open(image)  # use library PIL to see width and height
        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION
        if image.size > Product.MAX_SIZE_IMG:  # image.size - size of image | img.size - tuple of objects PIL(height...)
            raise ValidationError('Image size more than maximum allowed 3Mb')
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Image resolution less than minimum allowed!')
        if img.height > max_height or img.width > max_width:
            """if more than we cut img"""
            new_img = img.convert('RGB')
            resized_new_image = new_img.resize((450, 350), Image.ANTIALIAS)
            filestream = BytesIO()  # a variable that will convert an image into a data stream (bytes)
            resized_new_image.save(filestream, "JPEG", quality=90)
            filestream.seek(0)  # Moving to the 0(first) byte from the beginning of the file.
            new_name_resized_img = '{}'.format(image)
            image = InMemoryUploadedFile(
                filestream, "ImageField", new_name_resized_img, 'jpeg/image', sys.getsizeof(filestream), None
            )  # need to pass in InMemoryUploadedFile 6 args (file, field_name, name, content_type, size, charset)
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
admin.site.register(Order)
admin.site.register(Customer)
