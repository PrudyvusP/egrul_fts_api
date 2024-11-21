# egrul_fts_api

![egrul_fts_api workflow](https://github.com/PrudyvusP/egrul_fts_api/actions/workflows/main.yml/badge.svg)

**EGRUL FTS API** - сервис по работе с юридическими лицами
из [ЕГРЮЛ](https://clck.ru/373aau). Применяется как источник знаний для 
CRM-систем.
Сведения о ликвидированных организациях не обрабатываются.

---
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
---

### Установка

Установить проект:

```bash
git clone https://github.com/PrudyvusP/egrul_fts_api.git && cd "$(basename "$_" .git)"
```

Создать файл с переменными окружения, (пример [тут](https://github.com/PrudyvusP/egrul_fts_api/blob/main/.env.example)):

```bash
nano infra/.env
```

### Развертывание

Перейти в директорию *infra* и запустить последовательно
следующие команды от пользователя с правами **root**:

```bash
cd infra/
docker compose -p egrul up --build --d
docker compose -p egrul exec web python3 manage.py migrate
docker compose -p egrul exec web python3 manage.py collectstatic
```

Перейти по [адресу](http://localhost:28961/api/) и убедиться в работоспособности сервиса.

### Документация

Документация по стандарту OPENAPI доступна в виде [Redoc](http://localhost:28961/redoc/)
или [Swagger](http://localhost:28961/swagger/).

### Добавление данных

#### Реальные данные

Сведения из ЕГРЮЛ предоставляются ФНС России в формате XML
[установленным порядком](https://www.nalog.gov.ru/rn77/service/egrip2/access_order/).  
Сервис поддерживают обработку сведений из ЕГРЮЛ по форматам 405, 406 и 407.
Для этого используется команда `fill_egrul`.

```bash
docker compose -p egrul exec web python3 manage.py fill_egrul egrul_data/<path_to_dir_with_xml> -n <proc_num> [--update]
```

*egrul_data/<path_to_dir_with_xml>* - путь до директории с файлами XML; в текущем
виде [конфига](https://github.com/PrudyvusP/egrul_fts_api/blob/main/infra/docker-compose.yaml)
egrul_data монтируется в /tmp/.  
<proc_num> - количество процессов парсера.  
--update - признак обновления сведений.

#### Демонстрационные данные

Для демонстрации работы сервиса предусмотрена команда, которая создаст *N* вымышленных организаций

```bash
docker compose -p egrul exec web python3 manage.py fill_test_data <N>
```

### Особенности реализации полнотекстового поиска

Опытным путем на выборке из 3,2 млн записей в ЕГРЮЛ установлено, что более 80% организаций в ЕГРЮЛ - это
общества с ограниченной ответственностью, поэтому такие слова как "общество", "ограниченной" и "ответственностью"
были исключены из функции `ts_vector` при построении индекса, что позволило сократить память на хранение индекса на 24%.
При этом другие слова, например, "муниципальная" или "районная" или "государственное" нет смысла отбрасывать, так как
они могут нести физический смысл и на размер индекса сильно не влияют.
