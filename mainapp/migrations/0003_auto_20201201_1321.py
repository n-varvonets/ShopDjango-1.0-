# Generated by Django 3.1.3 on 2020-12-01 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_notebook_powerbanks_smartphone'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PowerBanks',
            new_name='Powerbank',
        ),
    ]
