from drf_yasg import openapi

MAIN_TAG = 'Организации'

RESPONSES_FOR_RETRIEVE_ORG = {
    '404': openapi.Response('Страница не найдена.',
                            examples={
                                "application/json": {
                                    "detail": "Страница не найдена."}
                            })
}

RESPONSES_FOR_FTS_SEARCH = {
    '400': openapi.Response('Не передан q.',
                            examples={
                                "application/json": {
                                    "detail": "Не передан обязательный "
                                              "параметр q."}
                            })
}
PARAMS_FOR_FTS_SEARCH = [
    openapi.Parameter("q",
                      openapi.IN_QUERY,
                      required=True,
                      description="Параметр полнотекстового поиска",
                      type=openapi.TYPE_STRING)
]

DOC_CONSTS = {
    "list":
        {
            "tags": [MAIN_TAG],
            "summary": "Список организаций",
            "description": ("Страница доступна всем пользователям. "
                            "Доступна фильтрация по ИНН, КПП, ОГРН."),
            "responses": []
        },
    "retrieve":
        {
            "tags": [MAIN_TAG],
            "summary": "Получение организации",
            "description": "Страница доступна всем пользователям.",
            "responses": RESPONSES_FOR_RETRIEVE_ORG
        },
    "list-fts":
        {
            "tags": [MAIN_TAG],
            "summary": "Список организаций по полнотекстовому поиску",
            "description": ('Страница доступна всем пользователям. Доступен '
                            'полнотекстовый поиск по параметру q.'),
            "responses": RESPONSES_FOR_FTS_SEARCH,
            "params": PARAMS_FOR_FTS_SEARCH
        }
}
