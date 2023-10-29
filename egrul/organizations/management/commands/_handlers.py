import abc
import datetime
import sys
from multiprocessing import Pool, RLock
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

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

    def save(self, orgs: Iterable['Organization']) -> None:
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

    Атрибуты класса
    ----------
    SUCCESS_CODE : int (по умолчанию - 0)
        Код успешного завершения обработки
    XML_NOT_FOUND_CODE : int (по умолчанию - -1)
        Код отсутствия хотя бы одного XML-файла ЕГРЮЛ
    status_codes
        Словарь типа "код статуса : текстовая информация статуса"

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
    handle() -> int
        Управляет обработкой сведениями из XML-файлов ЕГРЮЛ
    print_result(status_code: int) -> None
        Выводит в консоль сообщение по номеру кода
    divide_all_xml_into_equal_chunks(self, xml_files: List[Path])
     -> List[List[Path]]
        Разделяет объекты типа `Path` на равные куски
    create_jobs(pool: Pool, chunked_xml_paths: List[List[Path]])
        Возвращает список задач для процессов
        (список объектов multiprocessing.pool.ApplyResult)
    merge_results_from_jobs(self, jobs) -> Tuple[List[Dict], List[str]]
        Соединяет результаты выполнения задач
    interact_with_db(orgs_to_save, orgs_to_delete) -> None
        Взаимодействует с БД
    """
    SUCCESS_CODE: int = 0
    XML_NOT_FOUND_CODE: int = -1

    status_codes = {
        XML_NOT_FOUND_CODE: 'Ошибка! Не найдено подходящих XML-файлов!',
        SUCCESS_CODE: 'Успех!'
    }

    def __init__(self, cpu_count: int, dir_name: str, is_update: bool) -> None:
        self.cpu_count = cpu_count
        self.dir_name = dir_name
        self.is_update = is_update

    def print_result(self, status_code: int) -> None:
        """Выводит в консоль сообщение по номеру кода."""
        print(self.status_codes[status_code], file=sys.stdout)

    def divide_all_xml_into_equal_chunks(self,
                                         xml_files: List[Path]
                                         ) -> List[List[Path]]:
        """Разделяет объекты типа `Path` на равные куски."""
        chunk_len = len(xml_files) // self.cpu_count + 1
        return [
            xml_files[i:i + chunk_len]
            for i in range(0, len(xml_files), chunk_len)
        ]

    def create_jobs(self,
                    pool: Pool,
                    chunked_xml_paths: List[List[Path]]
                    ):
        """
        Возвращает список задач для процессов
        (список объектов multiprocessing.pool.ApplyResult).
        """
        jobs = []
        for chunked_xml_path in chunked_xml_paths:
            parser = XMLOrgParser(xml_files=chunked_xml_path,
                                  is_update=self.is_update)
            jobs.append(pool.apply_async(parser.parse))
        return jobs

    def merge_results_from_jobs(self, jobs) -> Tuple[List[Dict], List[str]]:
        """Соединяет и выводит в консоль результаты выполнения задач."""
        orgs_to_save = []
        orgs_to_delete = []

        for job in jobs:
            orgs_from_job, stats, orgs_to_delete_from_job = job.get()
            orgs_to_save.extend(orgs_from_job)
            orgs_to_delete.extend(orgs_to_delete_from_job)
            self.print_report(stats)
        return orgs_to_save, orgs_to_delete

    def interact_with_db(self, orgs_to_save, orgs_to_delete) -> None:
        """
        Взаимодействует с БД.
        Если передан флаг `self.is_update`, то из БД удаляются все организации
        по их ОГРН, которые встречаются в файлах обновлений ЕГРЮЛ
        (`orgs_to_delete`).
        В ином случае таблица с организациями очищается.
        В конечном итоге в БД сохраняются новые организации `orgs_to_save`.
        """
        with transaction.atomic():
            if self.is_update:
                OrgDeleter().delete(orgs_to_delete)
            else:
                Organization.truncate_ri()
            OrgSaver().save(orgs_to_save)

    def handle(self) -> int:
        """
        Управляет логикой обработки сведениями из XML-файлов ЕГРЮЛ.

        1) Ищем рекурсивно XML-файлы;
        2) Делим XML-файлы на равные куски в зависимости от кол-ва процессов;
        3) Создаем пул процессов;
        4) Создаем задачи для процессов;
        5) Запускаем задачи и соединяем результаты выполнения задач;
        6) Взаимодействуем с БД;
        7) Выводим сообщение об успешном завершении обработки.
        """
        xml_files = list(Path(self.dir_name).rglob('*.XML'))
        if not xml_files:
            self.print_result(self.XML_NOT_FOUND_CODE)
            return self.XML_NOT_FOUND_CODE
        chunked_xml_paths = self.divide_all_xml_into_equal_chunks(xml_files)
        pool = Pool(processes=self.cpu_count, initargs=(RLock(),))
        jobs = self.create_jobs(pool, chunked_xml_paths)
        orgs_to_save, orgs_to_delete = self.merge_results_from_jobs(jobs)
        self.interact_with_db(orgs_to_save, orgs_to_delete)
        self.print_result(self.SUCCESS_CODE)
        return self.SUCCESS_CODE


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

    def __init__(self, num: int):
        self.num = num

    def handle(self) -> int:
        """
        Управляет обработкой сведениями о демонстрационных организациях.
        Создает несуществующие реквизиты организаций, сохраняет их в БД,
        выводит отчетность.
        """
        parser = GenerateOrgParser(self.num)
        orgs, stats, ogrns_orgs_to_delete = parser.parse()
        OrgSaver().save(orgs)
        self.print_report(stats)
        return 0
