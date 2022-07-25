# egrul_fts_api

EGRUL FTS API - микросервис, который отдает основную информацию об организациях(-и)
из [Единого государственного реестра юридических лиц](https://ru.wikipedia.org/wiki/%D0%95%D0%B4%D0%B8%D0%BD%D1%8B%D0%B9_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%8E%D1%80%D0%B8%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D1%85_%D0%BB%D0%B8%D1%86).
Написан на Django-rest-framework, использует полнотекстовый поиск PostgreSQL.

Сервис отдает следующую информацию:
- полное наименование организации;
- сокращенное наименование организации;
- ИНН;
- ОГРН;
- фактический адрес;
- код региона.

Предполагается, что все сведения из ЕГРЮЛ расположены в XML-документах, доступ к которым
предоставляет Федеральная налоговая служба России в соответствии с
[установленным порядком](https://www.nalog.gov.ru/rn77/service/egrip2/access_order/).

