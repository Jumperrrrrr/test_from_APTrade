from django.db import models
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ValidationError


class Menu(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название меню',
        help_text='Уникальное название меню для использования в template tag'
    )
    
    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Меню'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название пункта'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Родительский пункт'
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='URL',
        help_text='Может быть явным URL (например: /page/) или named URL (например: page1)'
    )
    named_url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Named URL',
        help_text='Имя URL из urls.py (например: page1). Имеет приоритет над полем URL'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )
    
    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.parent and self.pk and self.parent.pk == self.pk:
            raise ValidationError({'parent': 'Пункт меню не может быть родителем самому себе'})
        
        if self.parent:
            parent = self.parent
            visited = {self.pk} if self.pk else set()
            while parent:
                if parent.pk and parent.pk in visited:
                    raise ValidationError({'parent': 'Обнаружена циклическая ссылка в дереве меню'})
                if parent.pk:
                    visited.add(parent.pk)
                parent = parent.parent
        
        if self.parent and not self.menu:
            self.menu = self.parent.menu
        elif self.parent and self.parent.menu and self.menu != self.parent.menu:
            self.menu = self.parent.menu
    
    def get_url(self):
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                return self.named_url
        elif self.url:
            return self.url
        return '#'
    
    def get_absolute_url(self):
        return self.get_url()
