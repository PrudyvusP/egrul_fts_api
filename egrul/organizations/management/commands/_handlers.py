import sys
import time
from multiprocessing import Pool, RLock
from pathlib import Path
from typing import Dict

from django.db import transaction

from ._base_deleter import OrgDeleter
from ._base_parser import OrgParser, XMLOrgParser
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
            org_parser: OrgParser,
            org_saver: OrgSaver,
            cpu_count: int,
            dir_name: str,
            org_deleter: OrgDeleter = None,

    ) -> None:
        self.parser = org_parser
        self.saver = org_saver
        self.deleter = org_deleter
        self.cpu_count = cpu_count
        self.dir_name = dir_name

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
        start = time.perf_counter()
        xml_files = list(Path(self.dir_name).glob('*.XML'))
        chunk_len = len(xml_files) // self.cpu_count + 1
        chunked_xml_paths = [
            xml_files[i:i + chunk_len] for i in range(0, len(xml_files), chunk_len)
        ]
        pool = Pool(processes=self.cpu_count, initargs=(RLock(),))
        jobs = []

        for chunked_xml_path in chunked_xml_paths:
            parser = XMLOrgParser(xml_files=chunked_xml_path, is_update=False)
            jobs.append(pool.apply_async(parser.parse))

        orgs_to_save = []
        orgs_to_delete = []
        for job in jobs:
            orgs_from_job, stats, orgs_to_delete_from_job = job.get()

            orgs_to_save.extend(orgs_from_job)
            orgs_to_delete.extend(orgs_to_delete_from_job)

        end = time.perf_counter()
        result = end - start

        if self.deleter:
            with transaction.atomic():
                self.deleter.delete(orgs_to_delete)
                self.saver.save(orgs_to_save)
        else:
            self.saver.save(orgs_to_save)
        print(result)
        # self.print_report(stats)
