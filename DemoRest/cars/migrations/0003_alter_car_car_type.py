# Generated by Django 3.2.1 on 2021-05-04 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_alter_car_car_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='car_type',
            field=models.IntegerField(choices=[(1, 'Седан'), (2, 'Хэчбек'), (3, 'Универсал'), (4, 'Купе'), (5, 'Чито-то еще')], verbose_name='Тип машины'),
        ),
    ]
