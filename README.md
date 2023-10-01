# egrul_fts_api

![egrul_fts_api workflow](https://github.com/PrudyvusP/egrul_fts_api/actions/workflows/main.yml/badge.svg)

EGRUL FTS API - микросервис, обрабатывающий информацию об организациях (юридических лицах)
из [Единого государственного реестра юридических лиц](https://ru.wikipedia.org/wiki/%D0%95%D0%B4%D0%B8%D0%BD%D1%8B%D0%B9_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%8E%D1%80%D0%B8%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D1%85_%D0%BB%D0%B8%D1%86):

- [x] полное наименование;
- [x] сокращенное наименование;
- [x] ИНН;
- [x] КПП;
- [x] ОГРН;
- [x] фактический адрес;
- [x] код региона;
- [ ] ОКВЭД;
- [ ] другие реквизиты и бухгалтерская отчетность.

Написан на Django-rest-framework, СУБД -
PostgreSQL + [полнотекстовый поиск](#Особенности-реализации-полнотекстового-поиска). В проекте
реализованы [API](#Документация), админка и [management-команды](#Добавление-данных).

### Применение

Сервис может использоваться как источник знаний для других продуктов,
например [cert_ecosystem](https://github.com/PrudyvusP/cert_ecosystem), с целью предоставления
пользователю возможности выбора из существующих организаций, а не создавать их самостоятельно, тем
самым существенно уменьшая вероятность наступления ошибок.

### Ограничения

- Сведения о ликвидированных организациях в сервисе не обрабатываются.
- В ЕГРЮЛ существуют организации с дублирующейся тройкой (ИНН, КПП, ОГРН). Логика работы сервиса
  предлагает отказаться от **филиалов** организаций, чьи КПП одинаковые.
- В админке выключено отображение списка всех организаций.

### Установка

Установить проект:

```bash
git clone https://github.com/PrudyvusP/egrul_fts_api.git && cd "$(basename "$_" .git)"
```

Создать файл *infra/.env*:

```
├── egrul
├── infra  
│   ├── nginx  
│   ├── .env                                <--- файл с переменными окружения
│   ├── docker-compose.yaml
│   └── extend_pg_tsearch_russian_dict.sh
├── .env.example 
├── .gitignore  
├── README.md  
└── setup.cfg  
```

Заполнить файл *infra/.env* (пример [тут](https://github.com/PrudyvusP/egrul_fts_api/blob/main/.env.example)).

### Развертывание

Перейти в директорию *infra* и запустить последовательно
следующие команды от пользователя с правами **root**:

```bash
docker-compose up --build --d
./extend_pg_tsearch_russian_dict.sh
docker exec -it infra_web_1 python3 manage.py migrate
docker exec -it infra_web_1 python3 manage.py collectstatic
```

Перейти по [адресу](http://localhost:28961/api/) и убедиться в работоспособности сервиса.

### Добавление данных

Сведения из ЕГРЮЛ расположены в XML-документах, доступ к которым
предоставляет ФНС России в соответствии
с [установленным порядком](https://www.nalog.gov.ru/rn77/service/egrip2/access_order/).  
Сведения из ЕГРЮЛ могут быть обработаны как по формату 405 (адреса в формате КЛАДР), так и по формату
406 (адреса в формате ФИАС).

Для использования реальных данных из ЕГРЮЛ предусмотрено использование команд `fill_egrul` и `update_egrul`:

```bash
docker exec -it infra_web_1 python3 manage.py fill_egrul egrul_data/<path_to_dir_with_xml>
docker exec -it infra_web_1 python3 manage.py update_egrul egrul_data/<path_to_dir_with_xml>
```

При этом *egrul_data/<path_to_dir_with_xml>* в текущем
виде [конфига](https://github.com/PrudyvusP/egrul_fts_api/blob/main/infra/docker-compose.yaml)
смонтируется в */tmp/<path_to_dir_with_xml>*, где должны лежать XML-файлы ЕГРЮЛ.

Для демонстрации логики работы сервиса предусмотрена команда, которая создаст *N*
относительно похожих на реальные данные строчек в БД:

```bash
docker exec -it infra_web_1 python3 manage.py fill_test_data <N>
```

### Документация

Документация по стандарту OPENAPI доступна в виде [Redoc](http://localhost:28961/api/redoc/)
или [Swagger](http://localhost:28961/api/swagger/).

### Особенности реализации полнотекстового поиска

Опытным путем на выборке из 3,2 млн записей в ЕГРЮЛ установлено, что более 80% организаций в ЕГРЮЛ - это
общества с ограниченной ответственностью, поэтому такие слова как "общество", "ограниченной" и "ответственностью"
были исключены из функции ts_vector при построении индекса, что позволило сократить память на хранение индекса на 24%.
При этом другие слова, например, "муниципальная" или "районная" или "государственное" нет смысла отбрасывать, так как
они могут нести физический смысл и на размер индекса сильно не влияют.

Для создания словаря при развертывании в docker
используется [bash-скрипт](https://github.com/PrudyvusP/egrul_fts_api/blob/main/infra/extend_pg_tsearch_russian_dict.sh),
а для изменения конфигурации полнотекстового поиска используется
[миграция](https://github.com/PrudyvusP/egrul_fts_api/blob/main/egrul/organizations/migrations/0002_create_fts_schema.py).
