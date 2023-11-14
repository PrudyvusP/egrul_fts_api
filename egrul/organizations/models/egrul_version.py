from django.db import models


class EgrulVersion(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    version = models.DateField()

    def __str__(self):
        return f'<Версия от {self.version}>'

    class Meta:
        db_table = 'egrul_version'
