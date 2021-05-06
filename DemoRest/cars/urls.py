from django.contrib import admin
from django.urls import path, include

# инклдим урлы в олдном основном месте с разных
from cars.views import *

app_name = 'car'
urlpatterns = [
    path('car/create/', CarCreateView.as_view()),
    path('all/', CarsListView.as_view()),
    path('car/detail/<int:pk>', CarDetailView.as_view())  # <int:pk> - берет одну единственную запись и отображает ее
]