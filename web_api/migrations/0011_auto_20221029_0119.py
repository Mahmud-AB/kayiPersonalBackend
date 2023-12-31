# Generated by Django 2.0.5 on 2022-10-28 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_api', '0010_auto_20220909_2223'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsorder',
            name='commission',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='users',
            name='commission',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
