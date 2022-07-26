# Generated by Django 4.0.6 on 2022-07-25 10:47

from django.contrib.postgres.search import SearchVector
from django.db import migrations


def compute_full_name_search(apps, schema_editor):
    organization = apps.get_model("organizations", "Organization")
    organization.objects.update(full_name_search=SearchVector("full_name", "short_name"))


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_organization_full_name_search_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            CREATE TRIGGER organizations_update_trigger
            BEFORE INSERT OR UPDATE OF full_name, short_name, full_name_search
            ON organizations_organization
            FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(
              full_name_search, 'pg_catalog.russian', full_name, short_name);

            UPDATE organizations_organization SET full_name_search = NULL;
            ''',

            reverse_sql='''
            DROP TRIGGER IF EXISTS organizations_update_trigger
            ON organizations_organization;
            '''),
        migrations.RunPython(
            compute_full_name_search, reverse_code=migrations.RunPython.noop
        ),
    ]