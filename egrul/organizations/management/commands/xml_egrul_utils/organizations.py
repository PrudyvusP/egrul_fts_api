from typing import Dict, List, Optional, Tuple

from lxml import etree

from .addresses import FIASEgrulAddress, KLADREgrulAddress


class EgrulUnitOrg:
    """
    Филиал организации.

    Используется для парсинга филиалов организаций в XML-файлах ЕГРЮЛ.
    ОГРН и ИНН должны быть такими же, как у юридического лица,
    на базе которого организован филиал.

    Атрибуты класса
    ----------
    address_fias_tag: str (по умолчанию - 'АдрМНФИАС')
        Наименование XML-тега, содержащего информацию
        об адресе филиала в формате ФИАС
    address_kladr_tag: str (по умолчанию - 'АдрМНРФ')
        Наименование XML-тега, содержащего информацию
        об адресе филиала в формате КЛАДР
    full_name_root_tag: str (по умолчанию - 'СвНаим')
        Наименование XML-тега, содержащего массив данных
         о наименовании филиала
    full_name_attrib: str (по умолчанию -'НаимПолн')
        Наименование XML-атрибута, содержащего наименование филиала
    kpp_root_tag: str (по умолчанию - 'СвУчетНОФилиал')
        Наименование XML-тега, содержащего массив данных
        о реквизитах филиала
    kpp_attrib: str (по умолчанию - 'КПП')
        Наименование XML-атрибута, содержащего информацию о КПП
    region_code_fias_tag: str (по умолчанию - 'Регион')
        Наименование XML-тега, содержащего код региона по формату ФИАС
    region_code_kladr_attrib: str (по умолчанию - 'КодРегион')
        Наименование XML-аттрибута, содержащего код региона по формату КЛАДР
    UNDEFINED_ADDRESS_TEXT: str (по умолчанию - 'НЕ УКАЗАН')
        Признак неуказанного в XML-файлах адреса
    UNDEFINED_REGION_CODE: str (по умолчанию - '00')
        Признак неопределенного кода региона

    Атрибуты экземпляра
    ----------
    unit_element : `etree.Element`
        Наименование XML-тега, содержащего массив данных
        о филиале
    ogrn: str
        ОГРН головной организации
    inn: str
        ИНН головной организации
    main_full_name: str
        Полное наименование головной организации

    Методы
    ----------
    get_full_name() -> str
        Возвращает полное наименование
    get_kpp() -> str
        Возвращает КПП
    get_address_and_region_code() -> Tuple[str, str]
        Возвращает фактический адрес и код региона
    get_props() -> Optional[Dict[str, str]]
        Возвращает словарь с реквизитами филиала
    """

    address_fias_tag: str = 'АдрМНФИАС'
    address_kladr_tag: str = 'АдрМНРФ'
    full_name_root_tag: str = 'СвНаим'
    full_name_attrib: str = 'НаимПолн'
    kpp_root_tag: str = 'СвУчетНОФилиал'
    kpp_attrib: str = 'КПП'
    region_code_fias_tag: str = 'Регион'
    region_code_kladr_attrib: str = 'КодРегион'

    UNDEFINED_ADDRESS_TEXT: str = 'НЕ УКАЗАН'
    UNDEFINED_REGION_CODE: str = '00'

    def __init__(self, unit_element: etree.Element, ogrn: str, inn: str,
                 main_full_name: str) -> None:
        self.unit_element = unit_element
        self.ogrn = ogrn
        self.inn = inn
        self.main_full_name = main_full_name

    def get_full_name(self) -> str:
        """Возвращает полное наименование филиала."""
        name = self.unit_element.find(self.full_name_root_tag)

        if etree.iselement(name):
            return name.attrib[self.full_name_attrib]
        return f'{self.main_full_name}. ФИЛИАЛ'

    def get_kpp(self) -> Optional[str]:
        """Возвращает КПП."""
        kpp = self.unit_element.find(self.kpp_root_tag)
        if etree.iselement(kpp):
            return kpp.attrib.get(self.kpp_attrib)
        return None

    def get_address_and_region_code(self) -> Tuple[str, str]:
        """Возвращает фактический адрес и код региона."""
        address_info = self.unit_element.find(self.address_fias_tag)

        if etree.iselement(address_info):
            region_code = address_info.find(self.region_code_fias_tag).text
            fias = FIASEgrulAddress(element=address_info,
                                    region_code=region_code)
            return fias.concat_address(), region_code

        address_info = self.unit_element.find(self.address_kladr_tag)
        if etree.iselement(address_info):
            region_code = (address_info.attrib.get(
                self.region_code_kladr_attrib,
                self.UNDEFINED_REGION_CODE)
            )
            kladr = KLADREgrulAddress(element=address_info,
                                      region_code=region_code)
            return " ".join(kladr.concat_address().split()), region_code

        return self.UNDEFINED_ADDRESS_TEXT, self.UNDEFINED_REGION_CODE

    def get_props(self) -> Optional[Dict[str, str]]:
        """Возвращает словарь с реквизитами филиала."""
        kpp = self.get_kpp()
        if not kpp:
            return None
        factual_address, region_code = self.get_address_and_region_code()
        return {
            'full_name': self.get_full_name(),
            'short_name': None,
            'ogrn': self.ogrn,
            'inn': self.inn,
            'kpp': kpp,
            'factual_address': factual_address,
            'region_code': region_code,
            'is_main': False
        }


class EgrulMainOrg:
    """
    Организация.

    Используется для парсинга организаций в XML-файлах ЕГРЮЛ.

    Атрибуты класса
    ----------
    address_fias_tag: str (по умолчанию - 'СвАдресЮЛ/СвАдрЮЛФИАС')
        Наименование XML-тега, содержащего информацию
        об адресе филиала в формате ФИАС
    address_kladr_tag: str (по умолчанию - 'СвАдресЮЛ/АдресРФ')
        Наименование XML-тега, содержащего информацию
        об адресе филиала в формате КЛАДР
    full_name_attrib: str (по умолчанию - 'НаимЮЛПолн')
        Наименование XML-атрибута, содержащего полное
        наименование организации
    inn_attrib: str (по умолчанию - 'ИНН')
        Наименование XML-атрибута, содержащего ИНН
    kpp_attrib: str (по умолчанию - 'КПП')
        Наименование XML-атрибута, содержащего КПП
    liquidated_tag: str (по умолчанию - 'СвПрекрЮЛ')
        Наименование XML-тега, содержащего массив данных
        о процессе ликвидации организации
    name_root_tag: str (по умолчанию - 'СвНаимЮЛ')
        Наименование XML-тега, содержащего массив данных
        о наименованиях организации
    ogrn_attrib: str (по умолчанию - 'ОГРН')
        Наименование XML-атрибута, содержащего ОГРН
    region_code_fias_tag: str (по умолчанию - 'Регион')
        Наименование XML-тега, содержащего код региона по формату ФИАС
    region_code_kladr_attrib: str (по умолчанию - 'КодРегион')
        Наименование XML-аттрибута, содержащего код региона по формату КЛАДР
    short_name_root_tag: str (по умолчанию - 'СвНаимЮЛСокр')
        Наименование XML-тега, содержащего массив данных
        о сокращенном наименовании организации
    short_name_attrib: str (по умолчанию - 'НаимСокр')
        Наименование XML-атрибута, содержащего сокращенное
        наименование организации
    units_root_tag: str (по умолчанию - 'СвПодразд')
        Наименование XML-тега, содержащего массив данных
        о филиалах организации
    unit_tag: str (по умолчанию - 'СвФилиал')
        Наименование XML-тега, содержащего массив данных
        о конкретном филиале организации
    MIN_SHORT_NAME_LEN: int (по умолчанию - 4)
        Минимальная длина (не включительно) сокращенного
        наименования организации
    UNDEFINED_REGION_CODE: str (по умолчанию - '00')
        Признак неопределенного кода региона

    Атрибуты экземпляра
    ----------
    element: `etree.Element`
        Наименование XML-тега, содержащего массив данных
        об организации

    Методы
    ----------
    is_liquidated() -> bool
        Определяет ликвидирована ли организация
    ogrn() -> str
        Свойство. Возвращает ОГРН
    inn() -> str
        Свойство. Возвращает ИНН
    kpp() -> str
        Свойство. Возвращает КПП
    full_name() -> str
        Свойство. Возвращает полное наименование.
    get_short_name(name_info: etree.Element) -> Optional[str]
        Возвращает сокращенное наименование
    get_address_and_region_code() -> Tuple[str, str]
        Возвращает фактический адрес и код региона
    has_units() -> bool
        Определяет есть ли филиалы у организации
    get_units() -> List[Dict[str, str]]
        Возвращает список словарей реквизитов филиалов организации.
    get_props() -> List[Dict[str, str]]
        Возвращает словарь с реквизитами организации и ее филиалов
    """

    address_fias_tag: str = 'СвАдресЮЛ/СвАдрЮЛФИАС'
    address_kladr_tag: str = 'СвАдресЮЛ/АдресРФ'
    full_name_attrib: str = 'НаимЮЛПолн'
    inn_attrib: str = 'ИНН'
    kpp_attrib: str = 'КПП'
    liquidated_tag: str = 'СвПрекрЮЛ'
    name_root_tag: str = 'СвНаимЮЛ'
    ogrn_attrib: str = 'ОГРН'
    region_code_fias_tag: str = 'Регион'
    region_code_kladr_attrib: str = 'КодРегион'
    short_name_root_tag: str = 'СвНаимЮЛСокр'
    short_name_attrib: str = 'НаимСокр'
    units_root_tag: str = 'СвПодразд'
    unit_tag: str = 'СвФилиал'

    MIN_SHORT_NAME_LEN: int = 4
    UNDEFINED_REGION_CODE: str = '00'

    abs_short_name_root_tag: str = name_root_tag + '/' + short_name_root_tag

    def __init__(self, element: etree.Element) -> None:
        self.element = element

    @property
    def is_liquidated(self) -> bool:
        """Возвращает True, если организация ликвидирована."""
        return etree.iselement(self.element.find(self.liquidated_tag))

    @property
    def ogrn(self) -> str:
        """Возвращает ОГРН."""
        return self.element.attrib[self.ogrn_attrib]

    @property
    def inn(self) -> str:
        """Возвращает ИНН."""
        return self.element.attrib.get(self.inn_attrib)

    @property
    def kpp(self) -> str:
        """Возвращает КПП."""
        return self.element.attrib.get(self.kpp_attrib)

    @property
    def full_name(self) -> str:
        """Возвращает полное наименование."""
        name_info = self.element.find(self.name_root_tag).attrib
        return name_info[self.full_name_attrib].strip()

    def get_short_name(self) -> Optional[str]:
        """Возвращает сокращенное наименование."""
        short_name_field = self.element.find(self.abs_short_name_root_tag)

        if (etree.iselement(short_name_field)
                and len(short_name_field.get(self.short_name_attrib)
                        ) > self.MIN_SHORT_NAME_LEN):
            return short_name_field.get(self.short_name_attrib)
        return None

    def get_address_and_region_code(self) -> Tuple[str, str]:
        """Возвращает фактический адрес и код региона.
        Приоритет отдается адресу по формату ФИАС.
        """
        main_address_info = self.element.find(self.address_fias_tag)
        if etree.iselement(main_address_info):
            region_code = main_address_info.find(
                self.region_code_fias_tag).text
            fias = FIASEgrulAddress(element=main_address_info,
                                    region_code=region_code)
            return fias.concat_address(), region_code

        main_address_info = self.element.find(self.address_kladr_tag)
        main_address_info_attrib = main_address_info.attrib
        region_code = main_address_info_attrib.get(
            self.region_code_kladr_attrib, self.UNDEFINED_REGION_CODE)
        kladr = KLADREgrulAddress(element=main_address_info,
                                  region_code=region_code)

        return " ".join(kladr.concat_address().split()), region_code

    def has_units(self) -> bool:
        """Возвращает True, если у организации есть филиалы."""
        return etree.iselement(self.element.find(self.units_root_tag))

    def get_units(self) -> List[Dict[str, str]]:
        """Возвращает список словарей реквизитов филиалов."""
        units = []

        if self.has_units():
            units_from_xml = (self.element
                              .find(self.units_root_tag)
                              .findall(self.unit_tag)
                              )
            for unit_from_xml in units_from_xml:
                new_unit = EgrulUnitOrg(
                    unit_element=unit_from_xml,
                    main_full_name=self.full_name,
                    inn=self.inn, ogrn=self.ogrn)
                new_unit = new_unit.get_props()
                if new_unit:
                    units.append(new_unit)
        return units

    def get_props(self) -> List[Dict[str, str]]:
        """
        Возвращает список словарей реквизитов организации и ее филиалов.
        """
        organizations = []
        factual_address, region_code = self.get_address_and_region_code()
        organizations.append(
            {
                'full_name': self.full_name,
                'short_name': self.get_short_name(),
                'ogrn': self.ogrn,
                'inn': self.inn,
                'kpp': self.kpp,
                'factual_address': factual_address,
                'region_code': region_code,
                'is_main': True
            }
        )
        for unit in self.get_units():
            organizations.append(unit)

        return organizations
