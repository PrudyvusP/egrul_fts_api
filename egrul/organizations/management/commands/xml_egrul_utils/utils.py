def get_str_with_deleted_hyphen(strq: str, length: int = 3) -> str:
    """Убирает лишний знак прочерка из адресной строки."""

    if len(strq) <= length:
        strq = strq.replace('-', '')
    if strq:
        strq += ', '
    return strq
