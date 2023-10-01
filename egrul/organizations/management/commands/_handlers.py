import sys
from typing import Type, Dict

from django.db import transaction

from ._base_deleter import OrgDeleter
from ._base_parser import OrgParser
from ._base_saver import OrgSaver


class Handler:
    """
    Хэндлер management-команд по заливанию сведений об организациях в БД.

    Атрибуты
    ----------
    parser : `OrgParser`
        Парсер организаций
    saver : `OrgSaver`
        Сохранятор организаций
    deleter : `OrgDeleter (по умолчанию None) `
        Удалятор организаций

    Методы
    -------
    handle()
        Выполняет основной метод класса
    print_report(stats: Dict[str, Dict[str, str]])
        Выводит отчетность
    """

    def __init__(
            self,
            org_parser: Type['OrgParser'],
            org_saver: Type['OrgSaver'],
            org_deleter: Type['OrgDeleter'] = None) -> None:
        self.parser = org_parser
        self.saver = org_saver
        self.deleter = org_deleter

    def print_report(self, stats: Dict[str, Dict[str, str]]):
        """
        Выводит информацию для отчетности.

        Параметры
        -------
        stats : Dict[str, Dict[str, str]]
            Словарь с исходными данными
        """

        for value in stats.values():
            print(f'{value["verbose_name"]}: {value["value"]}',
                  file=sys.stdout)

    def handle(self):
        """
        Управляет парсером, сохранятором и удалятором.
        """
        orgs_to_save, stats, orgs_to_delete = self.parser.parse()
        if self.deleter:
            with transaction.atomic():
                self.deleter.delete(orgs_to_delete)
                self.saver.save(orgs_to_save)
        else:
            self.saver.save(orgs_to_save)
        self.print_report(stats)
