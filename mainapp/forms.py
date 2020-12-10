from django import forms

from .models import Order


class OrderForm(forms.ModelForm):

    """date selection feature by clicking at the calendar """
    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Order  # specify model with which we working
        fields = (  # specify fields which we will render
            'first_name', 'last_name', 'phone', 'address',  'buying_type', 'order_date', 'comment'
        )

