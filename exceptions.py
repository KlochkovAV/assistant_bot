class ResponseError(Exception):
    """Отсутствует работа."""


class TokenNotFound(Exception):
    """Отсутствует токен."""


class RequestError(Exception):
    """Ошибка запроса."""