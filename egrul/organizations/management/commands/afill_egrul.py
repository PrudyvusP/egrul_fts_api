from pathlib import Path

from django.core.management.base import BaseCommand

from organizations.models import Organization
from ._base_parser import XMLOrgParser
from ._base_saver import OrgSaver
from ._handlers import Handler
from multiprocessing import Pool, RLock
from lxml import etree
def one_process_execution(pid, f_paths):

    res_arr = []

    for path in f_paths:
        tree = etree.parse(path)
        elements = tree.findall('СвЮЛ')
        for element in elements:
            if not etree.iselement(element.find('СвПрекрЮЛ')):
                orgs_from_xml = get_organization_objects(element)
                for org_from_xml in orgs_from_xml:
                    res_arr.append(org_from_xml)
    print(pid, 'stopped')
    return res_arr


class Command(BaseCommand):
    """Management-команда для заполнения информации
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Заполнят БД сведениями из ЕГРЮЛ'

    def add_arguments(self, parser):
        parser.add_argument('dir_name',
                            type=str,
                            help=('Путь до директории,'
                                  ' содержащей сведения из ЕГРЮЛ')
                            )
        parser.add_argument('n',
                            type=int,
                            default=4,
                            help=('Количество процессов'
                                  ' (по умолчанию: 4)')
                            )

    def handle(self, *args, **options):
        Organization.truncate_ri()
        dir_name = options.get('dir_name')
        proc_num = options.get('n')

        xml_paths = list(Path(dir_name).glob('*.XML'))
        chunk_len = len(xml_paths) // proc_num + 1
        inp_args = [xml_paths[i:i + chunk_len] for i in range(0, len(xml_paths), chunk_len)]
        inp_args = list(enumerate(inp_args))
        pool = Pool(processes=proc_num, initargs=(RLock(),))
        jobs = [pool.apply_async(one_process_execution, args=inp_arg) for inp_arg in inp_args]
        df_lists = list(map(lambda x: x.get(), jobs))

