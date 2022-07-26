# egrul_fts_api

![egrul_fts_api workflow](https://github.com/PrudyvusP/egrul_fts_api/actions/workflows/main.yml/badge.svg)


EGRUL FTS API - микросервис, который работает с основной информацией об организации(-ях)
из [Единого государственного реестра юридических лиц](https://ru.wikipedia.org/wiki/%D0%95%D0%B4%D0%B8%D0%BD%D1%8B%D0%B9_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%8E%D1%80%D0%B8%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D1%85_%D0%BB%D0%B8%D1%86).
Написан на Django-rest-framework, использует полнотекстовый поиск PostgreSQL.

Сервис работает со следующей информацией:
- полное наименование организации;
- сокращенное наименование организации;
- ИНН;
- ОГРН;
- фактический адрес;
- код региона.

Предполагается, что все сведения из ЕГРЮЛ расположены в XML-документах, доступ к которым
предоставляет Федеральная налоговая служба России в соответствии с
[установленным порядком](https://www.nalog.gov.ru/rn77/service/egrip2/access_order/).

### Использование
Сервис может использоваться как словарь данных для других сервисов, например [cert_ecosystem](https://github.com/PrudyvusP/cert_ecosystem),
в котором нет особого смысла использовать в работе более 10 млн записей из ЕГРЮЛ, а лишь работать
с определенным множеством организаций, размер которого ограничен несколькими тысячами.


### Management-команды

Для демонстрации логики работы сервиса предусмотрена команда, которая сгенерит 100 000 
относительно похожих на реальные данные строчек в БД:
```bash
docker-compose exec -T web python3 manage.py fill_test_data
```

Для использования реальных данных из ЕГРЮЛ, предусмотрено использование следующей команды:
```bash
docker-compose exec -T web python3 manage.py fill_egrul egrul_data/<path_to_dir_with_xml>
```
При этом ```egrul_data/<path_to_dir_with_xml>``` в текущем виде конфига
смонтируется в ```/tmp/<path_to_dir_with_xml>```, где должны лежать XML-файлы из ЕГРЮЛ


### Переменные окружения
Файл ```infra/.env``` должен содержать следующие переменные окружения:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=indonesia_Xena
BACKEND_HOSTS=localhost web 127.0.0.1 testserver
```

### Документация 
В настоящее время сервис поддерживает три endpoint'а: 

1) ```/api/organizations/```  
например, GET-запрос на ```/api/organizations/?page=2``` вернет что-то вроде:
```json
{
    "count": 100000,
    "next": "http://127.0.0.1/api/organizations/?page=3",
    "previous": "http://127.0.0.1/api/organizations/",
    "results": [
        {
            "full_name": "АКЦИОНЕРНОЕ ОБЩЕСТВО \"АВТОМОБИЛЬ\"",
            "short_name": "АО \"АВТОМОБИЛЬ\"",
            "inn": "550435143306",
            "url": "/api/organizations/129147/"
        },
        {
            "full_name": "АКЦИОНЕРНОЕ ОБЩЕСТВО \"АВТОМОБИЛЬ\"",
            "short_name": "АО \"АВТОМОБИЛЬ\"",
            "inn": "396462764649",
            "url": "/api/organizations/196174/"
        },
      ]
}
```

2) ```/api/organizations/<id>/```  
например, GET-запрос на ```/api/organizations/100043/``` вернет нечто похоже на:
```json
{
    "full_name": "ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"ЭПОХА\"",
    "short_name": "ПАО \"ЭПОХА\"",
    "inn": "205975495862",
    "ogrn": "4537933140928",
    "factual_address": "КУРГАНСКАЯ ОБЛАСТЬ, ДУХОВЩИНА, АЛЛЕЯ ПУДОВКИНА 441, 950378",
    "region_code": "74"
}
```

3) ```/api/organizations/fts-search/?q=<запрос к полнотекстовому поиску>```  
GET-запрос на подобный эндпоинт вернет найденные записи в БД точно в таком же формате 
как указано в п. 1).  
Параметр ```q``` обязателен.

### Примечание

В админке по адресу ```admin/organizations/organization/``` намеренно отключено отображение 
всех организаций за нецелесообразностью такового. Доступен поиск.

### Технологии

 - DRF
 - PostgreSQL
 - NGINX
 - Docker


### Рекомендации
Для локального развертывания в закрытом контуре (без использования подключения к сети "Интернет")
возможно с помощью команд ```docker pull```, ```docker save``` и ```docker load```
получить docker images с [Docker Hub](https://hub.docker.com/).

### TODO
Для реализации адекватного поиска по организациям целесообразно дополнить
русскоязычный словарь стоп-слов PostgreSQL словами "**общество**", "**акционерное**" и тд.