import os
import sys
import time
import logging

import requests
from requests import RequestException
from dotenv import load_dotenv
from telebot import TeleBot, apihelper

from exceptions import TokenNotFound, ResponseError, RequestError

load_dotenv(override=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s; %(levelname)s; %(message)s'
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности токенов."""
    vars = {
        'Токен практикума': PRACTICUM_TOKEN,
        'Токен телеграма': TELEGRAM_TOKEN,
    }
    miss_vars = []

    for name, element in vars.items():
        if element is None:
            logger.critical(f'Отсутствует токен {name}')
            miss_vars.append(name)
    if miss_vars:
        raise TokenNotFound(f'Не найден(ы) {', '.join(miss_vars)}')


def send_message(bot, message):
    """Отправка сообщений."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение успешно отправлено')
    except apihelper.ApiException as error:
        logger.error(f"Ошибка доступа к API: {error}")
    except RequestException as error:
        logger.error(f"Ошибка запроса: {error}")


def get_api_answer(timestamp):
    """Получение ответа от API."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except apihelper.ApiException:
        raise ResponseError('Ошибка доступа к Telegram API')
    except RequestException:
        raise RequestError('Ошибка запроса')
    if response.status_code != 200:
        raise ResponseError(f'Ошибка доступа: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    if not isinstance(response, dict):
        raise TypeError('Неожиданный тип данных')
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise KeyError('Ключ homeworks не обнаружен')
    if not isinstance(homeworks, list):
        raise TypeError('Неожиданный тип данных')
    return homeworks


def parse_status(homework):
    """Разделение статуса работы."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')

    for name, element in [
        ('homework_name', homework_name),
        ('status', status)
    ]:
        if element is None:
            raise KeyError(f'Отсутсвует {name}')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Неожиданный статус домашней работы')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    try:
        check_tokens()
    except TokenNotFound:
        sys.exit()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    old_message = None

    while True:

        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                timestamp = int(time.time())
                for homework in homeworks:
                    message = parse_status(homework)
                    if message != old_message:
                        send_message(bot, message)
                        old_message = message
            else:
                logger.debug('Обновления статуса нет')

        except Exception as error:
            if message != old_message:
                logger.error(f'Ошибка при запросе к основному API: {error}')
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                old_message = message

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
