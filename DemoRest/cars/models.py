from django.db import models

# беру встроенную юзеров из джанги след 2мя строками для форейн_кей машины
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.

class Car(models.Model):  # http://i.imgur.com/NOzwt17.png нужно обьязательно делать миграции
    vin = models.CharField(verbose_name='Вин', db_index=True, unique=True, max_length=64)  # для индекса фажно создать
    # уникальное значение,(http://i.imgur.com/4TwWaft.png) а то будет как на видео 1.10 и если нужно удалить
    # неуникальные записи, то ниже есть пример того как зайти в шел и удалить их
    color = models.CharField(verbose_name='Цвет', max_length=64)
    brand = models.CharField(verbose_name='Brand', max_length=64)
    CAR_TYPES = (
        (1, 'Седан'),
        (2, 'Хэчбек'),
        (3, 'Универсал'),
        (4, 'Купе'),
        (5, 'Чито-то еще'),
    )
    car_type = models.IntegerField(verbose_name='Тип машины', choices=CAR_TYPES)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)



# для удаления записей с бд если создал неуникальную запись
# ./manage.py shell
# from cars.models import Car
# Car.objects.all().delete()