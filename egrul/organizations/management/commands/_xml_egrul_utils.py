import xml.etree.ElementTree
from typing import List, Literal

from organizations.models import Organization
from ._regions_codes import regions


def cast_reg_pochta_to_constitute(region_name: str) -> str:
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


def get_geography_string(
        data_info: xml.etree.ElementTree.Element,
        _type: str,
        name: str,
        addr_format: Literal['KLADR', 'FIAS'] = 'KLADR') -> str:
    """Выбирает расположение ключевых слов адреса
    в строке по типу:
    Г. МОСКВА - для городов федерального значения,
    {Республика} Татарстан - для всего остального
    пустая строка - если поле не заполнено
    """

    if data_info is not None:
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


def line_formatter(strq: str, length: int) -> str:
    """Убирает лишний знак прочерка из адресной строки."""

    if len(strq) <= length:
        strq = strq.replace('-', '')
    if strq:
        strq += ', '
    return strq


def get_address(
        main_address_info: xml.etree.ElementTree.Element,
        region_code: str
) -> str:
    """Возвращает фактический адрес организации
     в виде строки из формата КЛАДР."""

    main_address_info_attrib = main_address_info.attrib
    index = main_address_info_attrib.get('Индекс', '000000')

    house = main_address_info_attrib.get('Дом', '')
    house = line_formatter(house, 2)
    building = main_address_info_attrib.get('Корпус', '')
    building = line_formatter(building, 2)
    flat = main_address_info_attrib.get('Кварт', '')
    flat = line_formatter(flat, 2)

    street = get_geography_string(main_address_info.find('Улица'),
                                  'ТипУлица',
                                  'НаимУлица')

    region = regions.get(region_code)
    if not region:
        region = get_geography_string(main_address_info.find('Регион'),
                                      'НаимРегион',
                                      'ТипРегион')
        region = region.replace(',', '').strip()
        region = cast_reg_pochta_to_constitute(region)
    region += ', '
    city = get_geography_string(main_address_info.find('Город'),
                                'ТипГород',
                                'НаимГород')

    locality = get_geography_string(main_address_info.find('НаселПункт'),
                                    'ТипНаселПункт',
                                    'НаимНаселПункт')

    return f'{street}{house}{building}{flat}{locality}{city}{region}{index}'


def get_fias_address(
        main_address_info: xml.etree.ElementTree.Element,
        region_code: str
) -> str:
    """Возвращает фактический адрес организации
     в виде строки из формата КЛАДР."""
    index = main_address_info.get('Индекс', '000000')

    region_name = regions.get(region_code)

    if not region_name:
        region_name = main_address_info.find('НаимРегион').text

        if region_name:
            if region_name.startswith('Г.'):
                region_name = region_name.upper().replace('Г.', 'Г. ')

    region_name += ', '

    city = get_geography_string(main_address_info.find('НаселенПункт'),
                                _type='Вид',
                                name='Наим',
                                addr_format='FIAS')

    street = get_geography_string(main_address_info.find('ЭлУлДорСети'),
                                  _type='Тип',
                                  name='Наим',
                                  addr_format='FIAS')

    house = get_geography_string(main_address_info.find('Здание'),
                                 _type='Тип',
                                 name='Номер',
                                 addr_format='FIAS')

    flat = get_geography_string(main_address_info.find('ПомещЗдания'),
                                _type='Тип',
                                name='Номер',
                                addr_format='FIAS')

    return f'{street}{house}{flat}{city}{region_name}{index}'


def get_organization_objects(
        element: xml.etree.ElementTree.Element
) -> List[Organization]:
    """Создает инстансы организации из переданного элемента."""

    organizations = []

    main_info = element.attrib
    name_info = element.find('СвНаимЮЛ').attrib
    full_name = name_info['НаимЮЛПолн'].strip()
    main_address_info = element.find('СвАдресЮЛ/СвАдрЮЛФИАС')
    if main_address_info is not None:
        region_code = main_address_info.find('Регион').text
        factual_address = get_fias_address(main_address_info, region_code)
    else:
        main_address_info = element.find('СвАдресЮЛ/АдресРФ')
        main_address_info_attrib = main_address_info.attrib
        region_code = main_address_info_attrib.get('КодРегион', '00')
        factual_address = get_address(main_address_info, region_code)
        factual_address = " ".join(factual_address.split())
    factual_address = factual_address.upper()
    short_name_field = element.find('СвНаимЮЛ/СвНаимЮЛСокр')
    if (short_name_field is not None
            and len(short_name_field.get('НаимСокр')) > 4):
        short_name = short_name_field.get('НаимСокр')
    else:
        short_name = name_info.get('НаимЮЛСокр')

    filial_flag = element.find('СвПодразд')

    if filial_flag is not None:
        branches_objects = []
        branches = filial_flag.findall('СвФилиал')

        for branch in branches:

            full_branch_name = branch.find('СвНаим')

            if full_branch_name is not None:
                full_branch_name = (f'{full_name}.'
                                    f' {full_branch_name.attrib["НаимПолн"]}')
            else:
                full_branch_name = f'{full_name}. ФИЛИАЛ'

            branch_address_info = branch.find('АдрМНФИАС')

            if branch_address_info is not None:
                branch_region_code = branch_address_info.find('Регион').text
                branch_main_address = get_fias_address(branch_address_info,
                                                       branch_region_code)
            else:
                branch_main_address = branch.find('АдрМНРФ')

                if branch_main_address is not None:
                    branch_region_code = (branch_main_address.attrib
                                          .get('КодРегион', '00')
                                          )
                    branch_main_address = get_address(branch_main_address,
                                                      region_code)
                else:
                    branch_main_address = 'НЕ УКАЗАН'
                    branch_region_code = '00'
            branch_kpp = branch.find('СвУчетНОФилиал')
            branch_main_address = branch_main_address.upper()
            # Если КПП у филиала отсутствует, то информация не льется в БД

            if branch_kpp is not None:
                branch_kpp = branch_kpp.attrib.get('КПП')
                branch_org = Organization(
                    full_name=full_branch_name,
                    inn=main_info.get('ИНН', None),
                    ogrn=main_info['ОГРН'],
                    kpp=branch_kpp,
                    region_code=branch_region_code,
                    factual_address=branch_main_address
                )
                branches_objects.append(branch_org)

        branches_objects = list(set(branches_objects))
        organizations.extend(branches_objects)
    new_org = Organization(
        full_name=full_name,
        short_name=short_name,
        inn=main_info.get('ИНН', None),
        ogrn=main_info['ОГРН'],
        kpp=main_info.get('КПП', None),
        factual_address=factual_address,
        region_code=region_code)
    organizations.append(new_org)
    return organizations


def get_organization_ogrn(
        element: xml.etree.ElementTree.Element
) -> str:
    return element.attrib['ОГРН']
