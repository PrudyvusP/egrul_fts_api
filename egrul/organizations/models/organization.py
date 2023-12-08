from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import connection, models


class Organization(models.Model):

    @classmethod
    def truncate_ri(cls):
        """TRUNCATE table_name RESTART IDENTITY."""
        with connection.cursor() as cur:
            cur.execute(f'TRUNCATE {cls._meta.db_table} RESTART IDENTITY')

    """Описание модели организации."""
    id = models.BigAutoField(primary_key=True,
                             help_text='Идентификатор организации в БД')

    full_name = models.TextField('Полное наименование',
                                 null=False, blank=False,
                                 help_text='Полное наименование организации')
    short_name = models.TextField(
        'Сокращенное наименование',
        null=True, blank=True,
        help_text='Сокращенное наименование организации')
    inn = models.CharField('ИНН', max_length=12,
                           null=True, blank=True,
                           db_index=True,
                           help_text='ИНН организации')
    ogrn = models.CharField('ОГРН', max_length=13,
                            db_index=True,
                            help_text='ОГРН организации')
    kpp = models.CharField('КПП', max_length=9,
                           null=True, blank=True,
                           db_index=True,
                           help_text='КПП организации')
    factual_address = models.TextField(
        'Адрес',
        help_text='Адрес местонахождения организации')
    full_name_search = SearchVectorField(null=True)
    region_code = models.CharField(
        'Код региона', max_length=3,
        null=True,
        help_text='Код региона в соответствии со справочником ФНС России')
    date_added = models.DateTimeField(
        auto_now=True,
        help_text='Дата внесения организации в БД')

    main = models.ForeignKey("self", on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name='branches')

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        indexes = [GinIndex(fields=['full_name_search'],
                            name='fts_gin_idx')]

    def __str__(self):
        return f'<{self.full_name} ОГРН {self.ogrn}, {self.inn}/{self.kpp}>'
