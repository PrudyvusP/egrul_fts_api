from abc import ABC, abstractmethod
from collections import OrderedDict

from lxml import etree

from .regions_codes import regions
from .utils import get_str_with_deleted_hyphen

FIAS_addr_parts = OrderedDict({
    'street': {
        'tag': 'ЭлУлДорСети',
        'type_attr_name': 'Тип',
        'value_attr_name': 'Наим'
    },
    'house': {
        'tag': 'Здание',
        'type_attr_name': 'Тип',
        'value_attr_name': 'Номер'
    },
    'flat': {
        'tag': 'ПомещЗдания',
        'type_attr_name': 'Тип',
        'value_attr_name': 'Номер'
    },
    'city': {
        'tag': 'НаселенПункт',
        'type_attr_name': 'Вид',
        'value_attr_name': 'Наим'
    }
})

KLADR_addr_parts = OrderedDict({
    'street': {
        'tag': 'Улица',
        'type_attr_name': 'ТипУлица',
        'value_attr_name': 'НаимУлица'
    },
    'locality': {
        'tag': 'НаселПункт',
        'type_attr_name': 'ТипНаселПункт',
        'value_attr_name': 'НаимНаселПункт'
    },
    'city': {
        'tag': 'Город',
        'type_attr_name': 'ТипГород',
        'value_attr_name': 'НаимГород'
    },
    'region': {
        'tag': 'Регион',
        'type_attr_name': 'НаимРегион',
        'value_attr_name': 'ТипРегион'
    },
    'house': {
        'tag': None,
        'type_attr_name': None,
        'value_attr_name': 'Дом'
    },
    'building': {
        'tag': None,
        'type_attr_name': None,
        'value_attr_name': 'Корпус'
    },
    'flat': {
        'tag': None,
        'type_attr_name': None,
        'value_attr_name': 'Кварт'
    }
})


class EgrulAddress(ABC):
    """
    Адрес нахождения организации из XML-файла.

    Атрибуты
    ----------
    element : `etree.Element`
        Наименование XML-тега, содержащего информацию об адресе
    region_code : str
        Код региона

    Методы
    -------
    concat_address()
        Абстрактный метод, реализующий стратегию конкатенации
        адресной строки при парсинге XML-тегов
    get_ordered_address_part(
                addr_part_element : `etree.Element`,
                _type : str,
                value : str)
        Упорядочивает элементы адресной строки
    type()
        Абстрактное свойство типа формата адреса
    """

    def __init__(self, element: etree.Element, region_code: str):
        self.element = element
        self.region_code = region_code

    @abstractmethod
    def concat_address(self):
        """Определяет стратегию конкатенации адресной строки,
        которую необходимо описать при наследовании."""

        pass

    @property
    @abstractmethod
    def type(self):
        """Определяет необходимость создания свойства,
        которое возвращает строку с типом адреса."""

        pass

    def get_ordered_address_part(
            self,
            addr_part_element: etree.Element,
            _type: str,
            value: str) -> str:
        """
        Собирает и возвращает часть адресной строки установленным порядком:
        [Г.] [НАИМЕНОВАНИЕ ГОРОДА ФЕДЕРАЛЬНОГО ЗНАЧЕНИЯ]
        [НАИМЕНОВАНИЕ ТИПА СУБЪЕКТА] [НАИМЕНОВАНИЕ СУБЪЕКТА]
        [ТИП НАСЕЛЕННОГО ПУНКТА] [НАИМЕНОВАНИЕ НАСЕЛЕННОГО ПУНКТА]
        [ТИП ЭЛЕМЕНТА АДРЕСА] [НАИМЕНОВАНИЕ ЭЛЕМЕНТА АДРЕСА].
        """

        if etree.iselement(addr_part_element):
            element_type = addr_part_element.attrib.get(_type, '')
            element_data = addr_part_element.attrib.get(value, '')

            # В структуре ФИАС иногда встречаются лишние точки.
            if self.type == 'FIAS':
                element_type = element_type.replace('.', '')
                element_type = element_type + '.'

            if element_data == 'ГОРОД':
                return f'Г. {element_type}, '

            return f'{element_type} {element_data}, '

        return ''


class FIASEgrulAddress(EgrulAddress):
    """
    Адрес нахождения организации из XML-файла по формату ФИАС.

    Методы
    -------
    concat_address()
        Возвращает строку с фактическим адресом организации
        по формату ФИАС
    type()
        свойство, возвращает строку "FIAS"
    """

    @property
    def type(self):
        return "FIAS"

    def concat_address(self) -> str:
        """Возвращает строку с фактическим адресом организации
         по формату ФИАС."""
        parts = []

        index = self.element.get('Индекс', '000000')
        region_name = (regions.get(self.region_code)
                       or self.element.find('НаимРегион').text) + ', '
        for value in FIAS_addr_parts.values():
            part = self.get_ordered_address_part(
                self.element.find(value['tag']),
                _type=value['type_attr_name'],
                value=value['value_attr_name']
            )
            parts.append(part)

        return f'{"".join(parts)}{region_name}{index}'.upper()


class KLADREgrulAddress(EgrulAddress):
    """
    Адрес нахождения организации из XML-файла по формату КЛАДР.

    Методы
    -------
    concat_address()
        Возвращает строку с фактическим адресом организации
        по формату КЛАДР
    cast_region_name(region_name : str)
        Статический метод. Приводит название региона к виду по Конституции РФ
    type()
        свойство, возвращает строку "KLADR"
    """

    @property
    def type(self):
        return "KLADR"

    @staticmethod
    def cast_region_name(region_name: str) -> str:
        """Преобразует название региона
         в соответствии со ст. 65 Конституцией РФ."""
        region = region_name.upper()
        if 'МОСКВА' in region:
            return 'Г. МОСКВА'
        if 'САНКТ' in region and 'ПЕТЕРБУРГ' in region:
            return 'Г. САНКТ-ПЕТЕРБУРГ'
        if 'КЕМЕРОВСКАЯ' in region:
            return 'КЕМЕРОВСКАЯ ОБЛАСТЬ - КУЗБАСС'
        if 'ЧУВАШИЯ' in region:
            return 'ЧУВАШСКАЯ РЕСПУБЛИКА - ЧУВАШИЯ'
        if 'ХАНТЫ' in region and 'МАНСИ' in region:
            return 'ХАНТЫ-МАНСИЙСКИЙ АВТОНОМНЫЙ ОКРУГ - ЮГРА'
        if 'ЯМАЛО' in region and 'НЕНЕЦКИЙ' in region:
            return 'ЯМАЛО-НЕНЕЦКИЙ АВТОНОМНЫЙ ОКРУГ'
        if 'СЕВАСТОПОЛЬ' in region:
            return 'Г. СЕВАСТОПОЛЬ'
        if 'РЕСПУБЛИКА' in region:
            if region.split()[0].endswith('КАЯ'):
                return region
            return f'РЕСПУБЛИКА {region.split("РЕСПУБЛИКА")[0].rstrip()}'

        return region

    def concat_address(self) -> str:
        """Возвращает строку с фактическим адресом организации
         по формату КЛАДР."""
        main_address_info_attrib = self.element.attrib
        index = main_address_info_attrib.get('Индекс', '000000')

        street = self.get_ordered_address_part(
            self.element.find(KLADR_addr_parts['street']['tag']),
            _type=KLADR_addr_parts['street']['type_attr_name'],
            value=KLADR_addr_parts['street']['value_attr_name'])

        house = main_address_info_attrib.get(
            KLADR_addr_parts['house']['value_attr_name'], '')
        house = get_str_with_deleted_hyphen(house)

        building = main_address_info_attrib.get(
            KLADR_addr_parts['building']['value_attr_name'], '')
        building = get_str_with_deleted_hyphen(building)

        flat = main_address_info_attrib.get(
            KLADR_addr_parts['flat']['value_attr_name'], '')
        flat = get_str_with_deleted_hyphen(flat)

        locality = self.get_ordered_address_part(
            self.element.find(KLADR_addr_parts['locality']['tag']),
            _type=KLADR_addr_parts['locality']['type_attr_name'],
            value=KLADR_addr_parts['locality']['value_attr_name'])

        city = self.get_ordered_address_part(
            self.element.find(KLADR_addr_parts['city']['tag']),
            _type=KLADR_addr_parts['city']['type_attr_name'],
            value=KLADR_addr_parts['city']['value_attr_name'])

        region = regions.get(self.region_code)
        if not region:
            region = self.get_ordered_address_part(
                self.element.find(KLADR_addr_parts['region']['tag']),
                _type=KLADR_addr_parts['region']['type_attr_name'],
                value=KLADR_addr_parts['region']['value_attr_name'])
            region = region.replace(',', '').strip()
            region = self.cast_region_name(region)
        region += ', '
        return (f'{street}{house}{building}{flat}'
                f'{locality}{city}{region}{index}'.upper())
