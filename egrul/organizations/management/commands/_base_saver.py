import datetime
from typing import Iterable

from django.core.exceptions import ObjectDoesNotExist

from organizations.models import Organization, EgrulVersion


class OrgSaver:
    """
    Сохранятор в БД сведений об организациях.

    Атрибуты
    ----------
    batch_size : int (по умолчанию 10 000)
        Максимальное количество сущностей на один `INSERT`

    Методы
    -------
    save(orgs: Iterable['Organization'])
        Порционно сохраняет сведения об организациях в БД
    """

    def __init__(self, batch_size: int = 10000) -> None:
        self.batch_size: int = batch_size

    def save(self, orgs: Iterable['Organization']):
        """
        Сохраняет в БД переданные организации и актуализирует
        дату внесения изменений в БД. Актуальная дата
        располагается всегда первой и единственной строкой
        в таблице `egrul_version`.

        Параметры
        -------
        orgs : Iterable['Organization']
            Последовательность организаций, которые необходимо сохранить в БД
        """

        if orgs:
            Organization.objects.bulk_create(orgs, batch_size=self.batch_size)
        try:
            version = EgrulVersion.objects.get(pk=1)
            version.version = datetime.date.today()
            version.save()
        except ObjectDoesNotExist:
            EgrulVersion.objects.create(id=1, version=datetime.date.today())
