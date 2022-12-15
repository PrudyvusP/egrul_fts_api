from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class Organization(models.Model):
    """Описание свойств организации."""

    full_name = models.TextField('Полное наименование',
                                 null=False, blank=False)
    short_name = models.TextField('Сокращенное наименование',
                                  null=True, blank=True)
    inn = models.CharField('ИНН', max_length=12,
                           null=True, blank=True,
                           db_index=True)
    ogrn = models.CharField('ОГРН', max_length=13,
                            unique=False, db_index=True)
    kpp = models.CharField('КПП', max_length=9,
                           null=True, blank=True,
                           db_index=True)
    factual_address = models.TextField('Адрес')
    full_name_search = SearchVectorField(null=True)
    region_code = models.CharField('Код региона', max_length=3,
                                   null=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        indexes = [GinIndex(fields=["full_name_search"],
                            name='organizations_names_gin')]
        constraints = [
            models.UniqueConstraint(
                fields=['inn', 'ogrn', 'kpp'],
                name='unique_organization')
        ]

    def __str__(self):
        return f'{self.full_name} ОГРН {self.ogrn}, {self.inn}/{self.kpp}'
