import abc
import datetime
import sys
from multiprocessing import Pool, RLock
from pathlib import Path
from typing import Dict, Iterable

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from organizations.models import EgrulVersion, Organization
from ._parsers import GenerateOrgParser, XMLOrgParser


class OrgDeleter:
    """
    Удалятор сведений об организациях.

    Методы
    -------
    delete(orgs_ogrns: Iterable['str'])
        Удаляет из БД организации, чьи ОГРН в последовательности `orgs_ogrns`
    """

    @staticmethod
    def delete(orgs_ogrns: Iterable[str]) -> None:
        """
        Удаляет сведения об организациях из БД по переданной
        последовательности ОГРН организаций.
        """

        Organization.objects.filter(ogrn__in=orgs_ogrns).delete()


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


class Handler(abc.ABC):
    """
    Обработчик сведений об организациях.

    Методы
    -------
    print_report(stats: Dict[str, Dict[str, str]])
        Выводит отчетность в консоль
    handle()
        Абстрактный метод обработки. При наследовании логику
        переопределить
    """

    @staticmethod
    def print_report(stats: Dict[str, Dict[str, str]]) -> None:
        """
        Выводит отчетность результата работы в консоль.

        Параметры
        -------
        stats : Dict[str, Dict[str, str]]
            Словарь с исходными данными
        """

        for value in stats.values():
            print(f'{value["verbose_name"]}: {value["value"]}',
                  file=sys.stdout)

    @abc.abstractmethod
    def handle(self):
        pass


class EgrulHandler(Handler):
    """
    Обработчик сведений об организациях из XML-файлов ЕГРЮЛ.

    Атрибуты
    ----------
    cpu_count : int
        Количество процессов парсинга XML-файлов ЕГРЮЛ
    dir_name : str
        Путь до XML-файлов ЕГРЮЛ
    is_update : bool
        Признак обновления или заполнения БД с нуля

    Методы
    -------
    handle()
        Управляет обработкой сведениями из XML-файлов ЕГРЮЛ
    """

    def __init__(self, cpu_count: int, dir_name: str, is_update: bool) -> None:
        self.cpu_count = cpu_count
        self.dir_name = dir_name
        self.is_update = is_update

    def handle(self):
        """
        Управляет обработкой сведениями из XML-файлов ЕГРЮЛ.
        Поддерживает два основных способа работы:
        если флаг `is_update = True`, то из БД удаляются все организации,
        которые присутствуют в файлах с обновлениями ЕГРЮЛ и заливаются
        только действующие организации. Если же флаг `is_update = False`,
        то БД очищается, и действующие организации заливаются в БД.
        """

        xml_files = list(Path(self.dir_name).rglob('*.XML'))
        chunk_len = len(xml_files) // self.cpu_count + 1
        chunked_xml_paths = [
            xml_files[i:i + chunk_len]
            for i in range(0, len(xml_files), chunk_len)
        ]
        pool = Pool(processes=self.cpu_count, initargs=(RLock(),))
        jobs = []

        for chunked_xml_path in chunked_xml_paths:
            parser = XMLOrgParser(xml_files=chunked_xml_path,
                                  is_update=self.is_update)
            jobs.append(pool.apply_async(parser.parse))

        orgs_to_save = []
        orgs_to_delete = []
        for job in jobs:
            orgs_from_job, stats, orgs_to_delete_from_job = job.get()

            orgs_to_save.extend(orgs_from_job)
            orgs_to_delete.extend(orgs_to_delete_from_job)
            self.print_report(stats)

        with transaction.atomic():
            if self.is_update:
                OrgDeleter().delete(orgs_to_delete)
                OrgSaver().save(orgs_to_save)
            else:
                Organization.truncate_ri()
                OrgSaver().save(orgs_to_save)


class TestDataHandler(Handler):
    """
    Обработчик сведений о демонстрационных организациях.

    Атрибуты
    ----------
    num : int
        Количество демонстрационных организаций

    Методы
    -------
    handle()
        Управляет обработкой сведениями
    """

    def __init__(self, num):
        self.num = num

    def handle(self):
        """
        Управляет обработкой сведениями о демонстрационных организациях.
        Создает несуществующие реквизиты организаций, сохранят их в БД,
        выводит отчетность.
        """

        parser = GenerateOrgParser(self.num)
        orgs, stats, ogrns_orgs_to_delete = parser.parse()
        OrgSaver().save(orgs)
        self.print_report(stats)
