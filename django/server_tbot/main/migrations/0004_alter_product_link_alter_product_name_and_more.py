# Generated by Django 4.2.1 on 2023-06-15 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_product_options_alter_product_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='link',
            field=models.CharField(max_length=200, verbose_name='ссылка'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Название товара'),
        ),
        migrations.AlterField(
            model_name='product',
            name='up_name',
            field=models.CharField(blank=True, max_length=250, verbose_name='Название товара в верхнем регистре'),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('name', 'description', 'link')},
        ),
    ]