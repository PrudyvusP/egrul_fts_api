# Generated by Django 4.0.6 on 2023-09-29 11:14

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id',
                 models.BigAutoField(help_text='Идентификатор организации в БД', primary_key=True, serialize=False)),
                ('full_name',
                 models.TextField(help_text='Полное наименование организации', verbose_name='Полное наименование')),
                ('short_name', models.TextField(blank=True, help_text='Сокращенное наименование организации', null=True,
                                                verbose_name='Сокращенное наименование')),
                ('inn',
                 models.CharField(blank=True, db_index=True, help_text='ИНН организации', max_length=12, null=True,
                                  verbose_name='ИНН')),
                ('ogrn',
                 models.CharField(db_index=True, help_text='ОГРН организации', max_length=13, verbose_name='ОГРН')),
                ('kpp',
                 models.CharField(blank=True, db_index=True, help_text='КПП организации', max_length=9, null=True,
                                  verbose_name='КПП')),
                ('factual_address',
                 models.TextField(help_text='Адрес местонахождения организации', verbose_name='Адрес')),
                ('full_name_search', django.contrib.postgres.search.SearchVectorField(null=True)),
                ('region_code',
                 models.CharField(help_text='Код региона в соответствии со справочником ФНС России', max_length=3,
                                  null=True, verbose_name='Код региона')),
                ('date_added', models.DateTimeField(auto_now=True, help_text='Дата внесения организации в БД')),
            ],
            options={
                'verbose_name': 'Организация',
                'verbose_name_plural': 'Организации',
            },
        ),
        migrations.AddIndex(
            model_name='organization',
            index=django.contrib.postgres.indexes.GinIndex(fields=['full_name_search'], name='fts_gin_idx'),
        ),
        migrations.AddConstraint(
            model_name='organization',
            constraint=models.UniqueConstraint(fields=('inn', 'ogrn', 'kpp'), name='unique_organization'),
        ),
    ]
