from pathlib import Path

from django.core.management.base import BaseCommand

from ._base_deleter import OrgDeleter
from ._base_parser import XMLOrgParser
from ._base_saver import OrgSaver
from ._handlers import Handler


class Command(BaseCommand):
    """Management-команда для внесения изменений
    об организациях ЕГРЮЛ из XML-файлов."""

    help = 'Вносит в БД изменения из ЕГРЮЛ'

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
        dir_name, proc_num = options.get('dir_name'), options.get('n')

        xml_files = Path(dir_name).glob('*.XML')
        handler = Handler(
            org_parser=XMLOrgParser(xml_files, is_update=True),
            org_saver=OrgSaver(),
            org_deleter=OrgDeleter(),
            cpu_count=proc_num,
            dir_name=dir_name
        )
        handler.handle()
