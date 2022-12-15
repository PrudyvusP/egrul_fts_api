import xml.etree.ElementTree
from typing import List

from .models import Organization


def get_geography_string(
        data_info: xml.etree.ElementTree.Element,
        _type: str,
        name: str) -> str:
    """Выбирает расположение ключевых слов адреса
    в строке по типу:
    г. Тестовый - для городов федерального значения,
    {Тип региона} название региона - для всего остального
    пустая строка - если поле не заполнено
    """

    if data_info is not None:
        data_info = data_info.attrib
        data_type = data_info.get(_type, '')
        data_name = data_info.get(name, '')
        if data_name.lower() == 'город':
            return f'{data_name} {data_type}, '
        return f'{data_type} {data_name}, '
    return ''


def get_address(
        main_address_info: xml.etree.ElementTree.Element
) -> str:
    """Возвращает фактический адрес организации
     в виде строки из формата КЛАДР."""

    main_address_info_attrib = main_address_info.attrib
    index = main_address_info_attrib.get('Индекс', '000000')

    house = main_address_info_attrib.get('Дом', '')
    house = house.replace('-', '')
    if house:
        house += ', '
    building = main_address_info_attrib.get('Корпус', '')
    building = building.replace('-', '')
    if building:
        building += ', '
    flat = main_address_info_attrib.get('Кварт', '')
    flat = flat.replace('-', '')
    if flat:
        flat += ', '

    street_info = main_address_info.find('Улица')
    street = get_geography_string(street_info,
                                  'ТипУлица',
                                  'НаимУлица')

    region_info = main_address_info.find('Регион')
    region = get_geography_string(region_info,
                                  'НаимРегион',
                                  'ТипРегион')
    city_info = main_address_info.find('Город')
    city = get_geography_string(city_info,
                                'ТипГород',
                                'НаимГород')
    locality_info = main_address_info.find('НаселПункт')
    locality = get_geography_string(locality_info,
                                    'ТипНаселПункт',
                                    'НаимНаселПункт')

    return f'{street}{house}{building}{flat} {region}{city}{locality}{index}'


def get_organization_objects(
        element: xml.etree.ElementTree.Element
) -> List[Organization]:
    """Создает инстансы организации из переданного элемента."""

    organizations = []

    main_info = element.attrib
    name_info = element.find('СвНаимЮЛ').attrib
    full_name = name_info['НаимЮЛПолн'].strip()

    main_address_info = element.find('СвАдресЮЛ/АдресРФ')

    main_address_info_attrib = main_address_info.attrib
    region_code = main_address_info_attrib.get('КодРегион', '00')
    factual_address = get_address(main_address_info)

    if name_info.get('НаимЮЛСокр') and len(name_info.get('НаимЮЛСокр')) < 4:
        short_name = None
    else:
        short_name = name_info.get('НаимЮЛСокр',
                                   name_info['НаимЮЛПолн']).strip()

    filial_flag = element.find('СвПодразд')

    if filial_flag:

        branches = filial_flag.findall('СвФилиал')

        for branch in branches:

            full_branch_name = branch.find('СвНаим')

            if full_branch_name:
                full_branch_name = f'{full_name}. {full_branch_name.attrib["НаимПолн"]}'
            else:
                full_branch_name = f'{full_name}. ФИЛИАЛ'

            branch_main_address = branch.find('АдрМНРФ')

            if branch_main_address:
                branch_region_code = branch_main_address.attrib.get('КодРегион', '00')
                branch_main_address = get_address(branch_main_address)
            else:
                branch_main_address = 'НЕ УКАЗАН'
                branch_region_code = '00'

            branch_kpp = branch.find('СвУчетНОФилиал')

            # Если КПП у филиала отсутствует, то информация не льется в БД

            if branch_kpp:
                branch_kpp = branch_kpp.attrib.get('КПП')
                branch_org = Organization(
                    full_name=full_branch_name,
                    inn=main_info.get('ИНН', None),
                    ogrn=main_info['ОГРН'],
                    kpp=branch_kpp,
                    region_code=branch_region_code,
                    factual_address=branch_main_address
                )
                organizations.append(branch_org)

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
