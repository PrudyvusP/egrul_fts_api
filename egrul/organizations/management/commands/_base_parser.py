import os
import random
import string
from abc import ABC, abstractmethod
from typing import Tuple, List, Dict

from lxml import etree
from mimesis import Generic
from mimesis.builtins import RussiaSpecProvider
from mimesis.locales import Locale

from organizations.models import Organization
from ._xml_egrul_utils import get_organization_objects, get_organization_ogrn


class OrgParser(ABC):
    """
    Парсер сведений об организациях.

    Методы
    -------
    parse()
        Абстрактный метод, реализующий логику сбора данных об организациях
    """

    @abstractmethod
    def parse(self, *args, **kwargs):
        """
        Определяет стратегию парсинга, которую необходимо описывать
        при наследовании.
        """

        pass


class XMLOrgParser(OrgParser):
    """
    Парсер сведений об организациях из XML-файлов.

    Атрибуты
    ----------
    dir_name : str
        Наименование директории, в которой расположены XML-файлы
    update : bool (по умолчанию False)
        Флажок для управления режимом залива/обновления сведений из ЕГРЮЛ

    Методы
    -------
    parse()
        Реализует логику сбора данных об организациях из XML-файлов
    """

    def __init__(self, dir_name: str, update: bool = False) -> None:
        self.dir_name = dir_name
        self.update = update

    def parse(
            self,
            *args,
            **kwargs
    ) -> Tuple[List['Organization'], Dict[str, Dict[str, str]], List[str]]:
        """
        Возвращает кортеж, состоящий из:
        [0] Список действующих организаций из XML-файлов ЕГРЮЛ,
         которые необходимо добавить в БД.
        [1] Словарь статистических штучек (сколько чего обработано, добавлено).
        [2] Список ОГРН организаций, подлежащих удалению.
        """

        orgs: List['Organization'] = []
        counter: int = 0
        counter_liq: int = 0
        counter_upd_new: int = 0
        ogrns_orgs_to_delete: List[str] = []

        for root, dirs, files in os.walk(self.dir_name):
            for file in files:
                file_path = os.path.join(root, file)
                counter += 1
                tree = etree.parse(file_path)
                elements = tree.findall('СвЮЛ')

                for element in elements:
                    if self.update:
                        ogrns_orgs_to_delete.append(
                            get_organization_ogrn(element)
                        )

                    if etree.iselement(element.find('СвПрекрЮЛ')):
                        counter_liq += 1
                    else:
                        orgs_from_xml = get_organization_objects(element)
                        counter_upd_new += len(orgs_from_xml)
                        for org_from_xml in orgs_from_xml:
                            orgs.append(org_from_xml)

        stats: Dict[str, Dict[str, str]] = {
            'counter': {
                "verbose_name": 'Обработано файлов',
                "value": counter
            },
            'counter_liq': {
                "verbose_name": 'Ликвидированных организаций пропущено',
                "value": counter_liq
            },
            'counter_new': {
                "verbose_name": ('Новых или измененных старых'
                                 ' организаций залито'),
                "value": counter_upd_new
            },
        }
        return orgs, stats, ogrns_orgs_to_delete


class GenerateOrgParser(OrgParser):
    """
    Создает приближенные к реальным данные об организациях.

    Атрибуты
    ----------
    num : int (по умолчанию 10 000)
        Количество организаций, которые нужно создать.

    Методы
    -------
    parse()
        Реализует логику генерации несуществующих организаций для демонстрации
    """

    forms: Dict[str, str] = {
        "ПАО": "ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО",
        "ОАО": "ОТКРЫТОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО",
        "АО": "АКЦИОНЕРНОЕ ОБЩЕСТВО",
        "ГУП": "ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ",
        "БУЗ": "БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ ЗДРАВООХРАНЕНИЯ",
        "АКБ": "АКЦИОНЕРНЫЙ КОММЕРЧЕСКИЙ БАНК",
        "ГК": "ГАРАЖНЫЙ КООПЕРАТИВ",
        "ООО": "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ",
        "НПО": "НАУЧНО-ПРОИЗВОДСТВЕННЫЙ КОМПЛЕКС",
        "ФКУ": "ФЕДЕРАЛЬНОЕ КАЗЕНОЕ УЧРЕЖДЕНИЕ"
    }

    def __init__(self, num: int = 10000):
        self.num = num

    def parse(
            self,
            *args,
            **kwargs
    ) -> Tuple[List['Organization'], Dict[str, Dict[str, str]], List[str]]:
        """
        Возвращает кортеж, состоящий из:
        [0] Список сгенерированных организаций, которые необходимо
        добавить в БД.
        [1] Словарь статистических штучек (сколько чего обработано, добавлено).
        [2] Список ОГРН организаций, подлежащих удалению.
        """

        orgs: List['Organization'] = []

        g = Generic(locale=Locale.RU)
        g.add_provider(RussiaSpecProvider)
        region_code_choices: str = string.digits
        short_names: Tuple[str] = tuple(self.forms.keys())

        for _ in range(self.num):
            address = (f'{g.address.address().upper()}, '
                       f'{g.address.city().upper()}, '
                       f'{g.address.region().upper()}, '
                       f'{g.address.zip_code()}')
            short_name_abbr: str = random.choice(short_names)
            full_name_abbr: str = self.forms[short_name_abbr]
            word: str = f'"{g.text.word().upper()}"'
            region_code: str = (random.choice(region_code_choices)
                                + random.choice(region_code_choices))
            org = Organization(
                inn=g.russia_provider.inn(),
                ogrn=g.russia_provider.ogrn(),
                kpp=g.russia_provider.kpp(),
                factual_address=address,
                region_code=region_code,
                short_name=f'{short_name_abbr} {word}',
                full_name=f'{full_name_abbr} {word}'

            )
            orgs.append(org)

        stats = {
            'counter_new': {
                "verbose_name": 'Сгенерированных организаций залито',
                "value": self.num
            }
        }
        return orgs, stats, []
