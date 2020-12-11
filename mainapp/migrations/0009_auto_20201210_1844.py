# Generated by Django 3.1.3 on 2020-12-10 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_auto_20201210_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='buying_type',
            field=models.CharField(choices=[('our_stores', 'from our stores '), ('courier_np', 'courier of NP to your address'), ('self_new_post', 'from the New Post Office'), ('self_new_ukr_post', 'from the UkrPost Office')], default='our_stores', max_length=100, verbose_name='Order status'),
        ),
    ]