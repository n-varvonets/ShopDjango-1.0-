from django.shortcuts import render
from rest_framework import generics
from cars.serializers import CarDetailSerializer, CarListSerializer
from cars.models import Car
from cars.permissions import IsOwnerOrReadOnly
# Create your views here.

class CarCreateView(generics.CreateAPIView):
    serializer_class = CarDetailSerializer

# отбразим созданные машины из бд при помощи след класса
class CarsListView(generics.ListAPIView):
    # ListAPIView должен обьязательно принимимать queryset(т.е. какие поля отображать из бд):
    serializer_class = CarListSerializer
    queryset = Car.objects.all()

#  для созданного обьекта(одной записи) в бд создадим его (*)RUD при просмотре
class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CarDetailSerializer  #  если мы одну запись просматриваем, то нам нужны все поля
    queryset = Car.objects.all()
    permission_classes = (IsOwnerOrReadOnly, )  # добавляем разрешение изменеия только тому юзеру, кто её(запись) создал


