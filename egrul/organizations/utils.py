import xml.etree.ElementTree

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


def get_organization_object(
        element: xml.etree.ElementTree.Element
) -> Organization:
    """Создает инстанс организации из переданного элемента."""

    main_info = element.attrib
    name_info = element.find('СвНаимЮЛ').attrib
    main_address_info = element.find('СвАдресЮЛ/АдресРФ').attrib
    full_name = name_info['НаимЮЛПолн'].strip()

    region_code = main_address_info.get('КодРегион', '00')
    index = main_address_info.get('Индекс', '000000')

    house = main_address_info.get('Дом', '')
    house = house.replace('-', '')
    if house:
        house += ', '
    building = main_address_info.get('Корпус', '')
    building = building.replace('-', '')
    if building:
        building += ', '
    flat = main_address_info.get('Кварт', '')
    flat = flat.replace('-', '')
    if flat:
        flat += ', '

    street_info = element.find('СвАдресЮЛ/АдресРФ/Улица')
    street = get_geography_string(street_info,
                                  'ТипУлица',
                                  'НаимУлица')

    region_info = element.find('СвАдресЮЛ/АдресРФ/Регион')
    region = get_geography_string(region_info,
                                  'НаимРегион',
                                  'ТипРегион')
    city_info = element.find('СвАдресЮЛ/АдресРФ/Город')
    city = get_geography_string(city_info,
                                'ТипГород',
                                'НаимГород')
    locality_info = element.find('СвАдресЮЛ/АдресРФ/НаселПункт')
    locality = get_geography_string(locality_info,
                                    'ТипНаселПункт',
                                    'НаимНаселПункт')

    factual_address = (f'{street}{house}{building}{flat}'
                       f'{region}{city}{locality}{index}')

    # print(factual_address)
    if name_info.get('НаимЮЛСокр') and len(name_info.get('НаимЮЛСокр')) < 4:
        short_name = None
    else:
        short_name = name_info.get('НаимЮЛСокр',
                                   name_info['НаимЮЛПолн']).strip()

    return Organization(
        full_name=full_name,
        short_name=short_name,
        inn=main_info.get('ИНН', None),
        ogrn=main_info['ОГРН'],
        factual_address=factual_address,
        region_code=region_code
    )


def get_organization_ogrn(
        element: xml.etree.ElementTree.Element
) -> str:
    return element.attrib['ОГРН']
