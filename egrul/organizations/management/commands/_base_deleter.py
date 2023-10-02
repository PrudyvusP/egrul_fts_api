from typing import Iterable

from organizations.models import Organization


class OrgDeleter:
    """
    Удалятор сведений об организациях.

    Методы
    -------
    delete(orgs_ogrns: Iterable['str'])
        Удаляет из БД организации, чьи ОГРН в последовательности `orgs_ogrns`
    """

    def delete(self, orgs_ogrns: Iterable[str]) -> None:
        """
        Удаляет сведения об организациях из БД по переданной
         последовательности ОГРН организаций.
        """

        Organization.objects.filter(ogrn__in=orgs_ogrns).delete()
