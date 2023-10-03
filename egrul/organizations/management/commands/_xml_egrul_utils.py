from typing import Literal, Tuple, Dict

from lxml import etree

from organizations.models import Organization
from ._regions_codes import regions


def line_formatter(strq: str, length: int) -> str:
    """Убирает лишний знак прочерка из адресной строки."""

    if len(strq) <= length:
        strq = strq.replace('-', '')
    if strq:
        strq += ', '
    return strq


def get_geography_string(
        data_info: etree.Element,
        _type: str,
        name: str,
        addr_format: Literal['KLADR', 'FIAS'] = 'KLADR') -> str:
    """
    Выбирает расположение ключевых слов адреса в строке по типу:
    Г.МОСКВА - для городов федерального значения, {Республика} Татарстан
     - для всего остального пустая строка - если поле не заполнено.
    """

    if etree.iselement(data_info):
        data_info = data_info.attrib

        data_type = data_info.get(_type, '')
        data_name = data_info.get(name, '')

        # В структуре ФИАС иногда встречаются лишние точки.
        if addr_format == 'FIAS':
            data_type = data_type.replace('.', '')
            data_type = data_type + '.'

        if data_name == 'ГОРОД':
            return f'Г. {data_type}, '
        return f'{data_type} {data_name}, '
    return ''


class Address:

    def __init__(self, element: etree.Element, region_code: str):
        self.element = element
        self.region_code = region_code

    def get_address(self):
        pass

    def cast_reg_pochta_to_constitute(self, region_name: str) -> str:
        """Преобразует название региона
         в соответствии со ст. 65 Конституцией РФ."""
        region = region_name.upper()
        if 'КЕМЕРОВСКАЯ' in region:
            return 'КЕМЕРОВСКАЯ ОБЛАСТЬ - КУЗБАСС'
        if 'ЧУВАШИЯ' in region:
            return 'ЧУВАШСКАЯ РЕСПУБЛИКА - ЧУВАШИЯ'
        if 'ХАНТЫ' in region and 'МАНСИ' in region:
            return 'ХАНТЫ-МАНСИЙСКИЙ АВТОНОМНЫЙ ОКРУГ - ЮГРА'
        if 'ЯМАЛО' in region and 'НЕНЕЦКИЙ' in region:
            return 'ЯМАЛО-НЕНЕЦКИЙ АВТОНОМНЫЙ ОКРУГ'
        if 'МОСКВА' in region:
            return 'Г. МОСКВА'
        if 'САНКТ' in region and 'ПЕТЕРБУРГ' in region:
            return 'Г. САНКТ-ПЕТЕРБУРГ'
        if 'СЕВАСТОПОЛЬ' in region:
            return 'Г. СЕВАСТОПОЛЬ'
        if 'РЕСПУБЛИКА' in region:
            if region.split()[0].endswith('КАЯ'):
                return region
            return f'РЕСПУБЛИКА {region.split("РЕСПУБЛИКА")[0].rstrip()}'

        return region


class FIASAddress(Address):
    def get_address(self) -> str:
        """Возвращает фактический адрес организации
         в виде строки из формата ФИАС."""
        index = self.element.get('Индекс', '000000')

        region_name = regions.get(self.region_code)

        if not region_name:
            region_name = self.element.find('НаимРегион').text

            if region_name:
                if region_name.startswith('Г.'):
                    region_name = region_name.upper().replace('Г.', 'Г. ')

        region_name += ', '

        city = get_geography_string(self.element.find('НаселенПункт'),
                                    _type='Вид',
                                    name='Наим',
                                    addr_format='FIAS')

        street = get_geography_string(self.element.find('ЭлУлДорСети'),
                                      _type='Тип',
                                      name='Наим',
                                      addr_format='FIAS')

        house = get_geography_string(self.element.find('Здание'),
                                     _type='Тип',
                                     name='Номер',
                                     addr_format='FIAS')

        flat = get_geography_string(self.element.find('ПомещЗдания'),
                                    _type='Тип',
                                    name='Номер',
                                    addr_format='FIAS')

        return f'{street}{house}{flat}{city}{region_name}{index}'.upper()


class KLADRAddress(Address):
    def get_address(self):
        """Возвращает фактический адрес организации
         в виде строки из формата КЛАДР."""

        main_address_info_attrib = self.element.attrib
        index = main_address_info_attrib.get('Индекс', '000000')

        house = main_address_info_attrib.get('Дом', '')
        house = line_formatter(house, 2)
        building = main_address_info_attrib.get('Корпус', '')
        building = line_formatter(building, 2)
        flat = main_address_info_attrib.get('Кварт', '')
        flat = line_formatter(flat, 2)

        street = get_geography_string(self.element.find('Улица'),
                                      'ТипУлица',
                                      'НаимУлица')

        region = regions.get(self.region_code)
        if not region:
            region = get_geography_string(self.element.find('Регион'),
                                          'НаимРегион',
                                          'ТипРегион')
            region = region.replace(',', '').strip()
            region = self.cast_reg_pochta_to_constitute(region)
        region += ', '
        city = get_geography_string(self.element.find('Город'),
                                    'ТипГород',
                                    'НаимГород')

        locality = get_geography_string(self.element.find('НаселПункт'),
                                        'ТипНаселПункт',
                                        'НаимНаселПункт')

        return (f'{street}{house}{building}{flat}'
                f'{locality}{city}{region}{index}'.upper()
                )


class EgrulUnitOrg:
    def __init__(self,
                 unit_element: etree.Element,
                 ogrn: str,
                 inn: str,
                 main_full_name: str,
                 full_name_root_tag: str = 'СвНаим',
                 full_name_tag: str = 'НаимПолн',
                 kpp_root_tag: str = 'СвУчетНОФилиал',
                 kpp_tag: str = 'КПП',
                 address_fias_tag: str = 'АдрМНФИАС',
                 address_kladr_tag: str = 'АдрМНРФ',
                 ):
        self.unit_element = unit_element
        self.ogrn = ogrn
        self.inn = inn
        self.main_full_name = main_full_name
        self.full_name_root_tag = full_name_root_tag
        self.full_name_tag = full_name_tag
        self.kpp_root_tag = kpp_root_tag
        self.kpp_tag = kpp_tag
        self.address_fias_tag = address_fias_tag
        self.address_kladr_tag = address_kladr_tag

    def get_full_name(self) -> str:
        """Возвращает полное наименование."""
        name = self.unit_element.find(self.full_name_root_tag)

        if etree.iselement(name):
            return f'{self.main_full_name}. {name.attrib[self.full_name_tag]}'
        return f'{self.main_full_name}. ФИЛИАЛ'

    def get_ogrn(self) -> str:
        """Возвращает ОГРН."""
        return self.ogrn

    def get_inn(self) -> str:
        """Возвращает ИНН."""
        return self.inn

    def get_kpp(self) -> str:
        """Возвращает КПП."""
        branch_kpp = self.unit_element.find(self.kpp_root_tag)
        if etree.iselement(branch_kpp):
            return branch_kpp.attrib.get(self.kpp_tag)

    def get_address_and_region_code(self) -> Tuple[str, str]:
        """Возвращает фактический адрес и код региона."""

        address_info = self.unit_element.find(self.address_fias_tag)

        if etree.iselement(address_info):
            region_code = address_info.find('Регион').text
            fias = FIASAddress(element=address_info, region_code=region_code)
            return fias.get_address(), region_code

        address_info = self.unit_element.find(self.address_kladr_tag)
        if etree.iselement(address_info):
            region_code = (address_info.attrib
                           .get('КодРегион', '00')
                           )
            kladr = KLADRAddress(element=address_info, region_code=region_code)
            return kladr.get_address(), region_code
        return 'НЕ УКАЗАН', '00'

    def get_props(self) -> Dict[str, str]:
        """
        full_name, ogrn, inn, kpp, factual_address, region_code.
        """
        kpp = self.get_kpp()
        # Если КПП у филиала отсутствует, то информация не льется в БД
        if not kpp:
            return {}

        factual_address, region_code = self.get_address_and_region_code()
        return {
            'full_name': self.get_full_name(),
            'short_name': None,
            'ogrn': self.get_ogrn(),
            'inn': self.get_inn(),
            'kpp': kpp,
            'factual_address': factual_address,
            'region_code': region_code,
        }


class EgrulMainOrg:
    def __init__(self, element: etree.Element,
                 ogrn_tag: str = 'ОГРН',
                 inn_tag: str = 'ИНН',
                 kpp_tag: str = 'КПП',
                 name_root_tag: str = 'СвНаимЮЛ',
                 full_name_tag: str = 'НаимЮЛПолн',
                 units_root_tag: str = 'СвПодразд',
                 unit_tag: str = 'СвФилиал',
                 ) -> None:
        self.element = element
        self.ogrn_tag = ogrn_tag
        self.inn_tag = inn_tag
        self.kpp_tag = kpp_tag
        self.name_root_tag = name_root_tag
        self.full_name_tag = full_name_tag
        self.units_root_tag = units_root_tag
        self.unit_tag = unit_tag

    @property
    def ogrn(self) -> str:
        """Возвращает ОГРН."""
        return self.element.attrib[self.ogrn_tag]

    @property
    def inn(self) -> str:
        """Возвращает ИНН."""
        return self.element.attrib.get(self.inn_tag)

    @property
    def kpp(self) -> str:
        """Возвращает КПП."""
        return self.element.attrib.get(self.kpp_tag)

    def get_full_name(self) -> str:
        """Возвращает полное наименование"""
        name_info = self.element.find(self.name_root_tag).attrib
        return name_info[self.full_name_tag].strip()

    def get_short_name(self, name_info: etree.Element) -> str:
        """Возвращает сокращенное наименование."""
        short_name_field = self.element.find('СвНаимЮЛ/СвНаимЮЛСокр')
        if (etree.iselement(short_name_field)
                and len(short_name_field.get('НаимСокр')) > 4):
            return short_name_field.get('НаимСокр')
        return name_info.get('НаимЮЛСокр')  # TODO надо подумать чо с этими тегами делать

    def get_address_and_region_code(
            self
    ) -> Tuple[str, str]:
        """Возвращает фактический адрес и код региона."""
        main_address_info = self.element.find('СвАдресЮЛ/СвАдрЮЛФИАС')

        if etree.iselement(main_address_info):
            region_code = main_address_info.find('Регион').text
            fias = FIASAddress(element=main_address_info, region_code=region_code)
            return fias.get_address(), region_code
        main_address_info = self.element.find('СвАдресЮЛ/АдресРФ')
        main_address_info_attrib = main_address_info.attrib
        region_code = main_address_info_attrib.get('КодРегион', '00')
        kladr = KLADRAddress(element=main_address_info, region_code=region_code)
        address = kladr.get_address()
        return " ".join(address.split()), region_code

    def has_branches(self) -> bool:
        """Возвращает True, если есть тег с филиалами."""
        return etree.iselement(self.element.find(self.units_root_tag))

    def get_props(self):
        """
        full_name, short_name, factual_address, region_code,
        inn, ogrn, kpp.
        """
        organizations = []

        name_info = self.element.find('СвНаимЮЛ').attrib
        full_name = self.get_full_name()
        factual_address, region_code = self.get_address_and_region_code()

        organizations.append(
            {
                'full_name': self.get_full_name(),
                'short_name': self.get_short_name(name_info),
                'ogrn': self.ogrn,
                'inn': self.inn,
                'kpp': self.kpp,
                'factual_address': factual_address,
                'region_code': region_code,
            }
        )

        if self.has_branches():

            units = (self.element
                     .find(self.units_root_tag)
                     .findall(self.unit_tag)
                     )

            for unit in units:
                new_unit = EgrulUnitOrg(unit, ogrn=self.ogrn,
                                        inn=self.inn, main_full_name=full_name)
                organizations.append(new_unit.get_props())

        return organizations


def get_organization_ogrn(
        element: etree.Element
) -> str:
    return element.attrib['ОГРН']


def get_organizations_from_xml(file_path, is_update):
    organizations = []
    organizations_to_delete = []

    tree = etree.parse(file_path)
    elements = tree.findall('СвЮЛ')

    for element in elements:
        if is_update:
            organizations_to_delete.append(
                get_organization_ogrn(element)
            )

        if not etree.iselement(element.find('СвПрекрЮЛ')):
            egrul_orgs = EgrulMainOrg(element=element)
            parsed_orgs = egrul_orgs.get_props()
            for parsed_org in parsed_orgs:
                organizations.append(
                    Organization(
                        **parsed_org
                    )
                )
    return organizations, organizations_to_delete
