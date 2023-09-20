from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название товара')
    price = models.CharField(max_length=30, verbose_name='Цена', blank=True)
    description = models.TextField(blank=True, verbose_name='Описание товара')
    link = models.CharField(max_length=200, verbose_name='ссылка')
    up_name = models.CharField(max_length=250, verbose_name='Название товара в верхнем регистре', blank=True)

    class Meta:
        unique_together = ('name', 'description', 'link')
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.name}'




