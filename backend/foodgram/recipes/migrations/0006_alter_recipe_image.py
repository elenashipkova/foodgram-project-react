# Generated by Django 3.2.9 on 2022-01-29 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20220129_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='recipes/images/', verbose_name='Фото рецепта'),
        ),
    ]
