from django.db import models


class EgrulVersion(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    version = models.DateField()

    class Meta:
        db_table = 'egrul_version'
