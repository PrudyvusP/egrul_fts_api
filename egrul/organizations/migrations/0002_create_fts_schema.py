# Generated by Django 4.0.6 on 2023-09-17 18:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            CREATE TEXT SEARCH CONFIGURATION public.russian_egrul (copy=pg_catalog.russian);
            
            CREATE TEXT SEARCH DICTIONARY public.russian_custom_dict (
            template=snowball,
            language=russian,
            stopwords=russian_extended);
            
            ALTER TEXT SEARCH CONFIGURATION public.russian_egrul
            ALTER MAPPING FOR hword, hword_part, word
                WITH russian_custom_dict;
            ''',

            reverse_sql='''
            DROP TEXT SEARCH CONFIGURATION public.russian_egrul;
            DROP TEXT SEARCH DICTIONARY public.russian_custom_dict;
            '''),
    ]