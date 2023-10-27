from typing import Dict, List, Optional, Tuple

from lxml import etree

from .addresses import FIASEgrulAddress, KLADREgrulAddress


class EgrulUnitOrg:
    """
    Филиал организации в XML-файлах ЕГРЮЛ.

    Атрибуты
    ----------
    unit_element : `etree.Element`
        Наименование XML-тега, содержащего массив данных
        о филиале
    ogrn: str
        ОГРН
    inn: str
        ИНН
    main_full_name: str
        Полное наименование
    full_name_root_tag: str (по умолчанию - 'СвНаим')
        Наименование XML-тега, содержащего массив данных
         о наименовании филиала
    full_name_tag: str (по умолчанию -'НаимПолн')
        Наименование XML-тега, содержащего наименование филиала
    kpp_root_tag: str (по умолчанию - 'СвУчетНОФилиал')
        Наименование XML-тега, содержащего массив данных
        о реквизитах филиала
    kpp_tag: str (по умолчанию - 'КПП')
        Наименование XML-тега, содержащего информацию о КПП
    address_fias_tag: str (по умолчанию - 'АдрМНФИАС')
        Наименование XML-тега, содержащего информацию
        об адресе филиала в формате ФИАС
    address_kladr_tag: str (по умолчанию - 'АдрМНРФ')
        Наименование XML-тега, содержащего информацию
        об адресе филиала в формате КЛАДР

    Методы
    -------
    get_full_name() -> str
        Возвращает полное наименование
    get_ogrn() -> str
        Возвращает ОГРН
    get_inn() -> str
        Возвращает ИНН
    get_kpp() -> str
        Возвращает КПП
    get_address_and_region_code() -> Tuple[str, str]
        Возвращает фактический адрес и код региона
    get_props() -> Optional[Dict[str, str]]
        Возвращает словарь с реквизитами филиала
    """

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
        kpp = self.unit_element.find(self.kpp_root_tag)
        if etree.iselement(kpp):
            return kpp.attrib.get(self.kpp_tag)

    def get_address_and_region_code(self) -> Tuple[str, str]:
        """Возвращает фактический адрес и код региона."""

        address_info = self.unit_element.find(self.address_fias_tag)

        if etree.iselement(address_info):
            region_code = address_info.find('Регион').text
            fias = FIASEgrulAddress(element=address_info,
                                    region_code=region_code)
            return fias.concat_address(), region_code
        address_info = self.unit_element.find(self.address_kladr_tag)
        if etree.iselement(address_info):
            region_code = (address_info.attrib
                           .get('КодРегион', '00')
                           )
            kladr = KLADREgrulAddress(element=address_info,
                                      region_code=region_code)
            return kladr.concat_address(), region_code
        return 'НЕ УКАЗАН', '00'

    def get_props(self) -> Optional[Dict[str, str]]:
        """Возвращает словарь с реквизитами филиала."""
        kpp = self.get_kpp()
        if not kpp:
            return None
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
    """
    Организация в XML-файлах ЕГРЮЛ.

    Атрибуты
    ----------
    element: `etree.Element`
        Наименование XML-тега, содержащего массив данных
        об организации
    ogrn_tag: str (по умолчанию - 'ОГРН')
        Наименование XML-тега, содержащего ОГРН
    inn_tag: str (по умолчанию - 'ИНН')
        Наименование XML-тега, содержащего ИНН
    kpp_tag: str (по умолчанию - 'КПП')
        Наименование XML-тега, содержащего КПП
    liquidated_tag: str (по умолчанию - 'СвПрекрЮЛ')
        Наименование XML-тега, содержащего массив данных
        о процессе ликвидации организации
    name_root_tag: str (по умолчанию - 'СвНаимЮЛ')
        Наименование XML-тега, содержащего массив данных
        о наименованиях организации
    full_name_tag: str (по умолчанию - 'НаимЮЛПолн')
        Наименование XML-тега, содержащего полное
        наименование организации
    units_root_tag: str (по умолчанию - 'СвПодразд')
        Наименование XML-тега, содержащего массив данных
        о филиалах организации
    unit_tag: str (по умолчанию - 'СвФилиал')
        Наименование XML-тега, содержащего массив данных
        о конкретном филиале организации

    Методы
    -------

    -------
    """

    def __init__(self,
                 element: etree.Element,
                 ogrn_tag: str = 'ОГРН',
                 inn_tag: str = 'ИНН',
                 kpp_tag: str = 'КПП',
                 liquidated_tag: str = 'СвПрекрЮЛ',
                 name_root_tag: str = 'СвНаимЮЛ',
                 full_name_tag: str = 'НаимЮЛПолн',
                 units_root_tag: str = 'СвПодразд',
                 unit_tag: str = 'СвФилиал',
                 ) -> None:
        self.element = element
        self.ogrn_tag = ogrn_tag
        self.inn_tag = inn_tag
        self.kpp_tag = kpp_tag
        self.liquidated_tag = liquidated_tag
        self.name_root_tag = name_root_tag
        self.full_name_tag = full_name_tag
        self.units_root_tag = units_root_tag
        self.unit_tag = unit_tag

    @property
    def is_liquidated(self) -> bool:
        """Возвращает True, если организация ликвидирована."""
        return etree.iselement(self.element.find(self.liquidated_tag))

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

    @property
    def full_name(self) -> str:
        """Возвращает полное наименование."""
        name_info = self.element.find(self.name_root_tag).attrib
        return name_info[self.full_name_tag].strip()

    def get_short_name(self, name_info: etree.Element) -> str:
        """Возвращает сокращенное наименование."""
        short_name_field = self.element.find('СвНаимЮЛ/СвНаимЮЛСокр')
        if (etree.iselement(short_name_field)
                and len(short_name_field.get('НаимСокр')) > 4):
            return short_name_field.get('НаимСокр')
        # TODO надо подумать чо с этими тегами делать
        return name_info.get('НаимЮЛСокр')

    def get_address_and_region_code(
            self
    ) -> Tuple[str, str]:
        """Возвращает фактический адрес и код региона."""
        main_address_info = self.element.find('СвАдресЮЛ/СвАдрЮЛФИАС')
        if etree.iselement(main_address_info):
            region_code = main_address_info.find('Регион').text
            fias = FIASEgrulAddress(element=main_address_info,
                                    region_code=region_code)
            return fias.concat_address(), region_code
        main_address_info = self.element.find('СвАдресЮЛ/АдресРФ')
        main_address_info_attrib = main_address_info.attrib
        region_code = main_address_info_attrib.get('КодРегион', '00')
        kladr = KLADREgrulAddress(element=main_address_info,
                                  region_code=region_code)
        return " ".join(kladr.concat_address().split()), region_code

    def has_units(self) -> bool:
        """Возвращает True, если в XML встречается тег с филиалами."""
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

        name_info = self.element.find(self.name_root_tag).attrib
        factual_address, region_code = self.get_address_and_region_code()

        organizations.append(
            {
                'full_name': self.full_name,
                'short_name': self.get_short_name(name_info),
                'ogrn': self.ogrn,
                'inn': self.inn,
                'kpp': self.kpp,
                'factual_address': factual_address,
                'region_code': region_code,
            }
        )
        for unit in self.get_units():
            organizations.append(unit)

        return organizations
