import os
import sys
import time
import logging

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import TokenNotFound, HomeworkNotFound

load_dotenv(override=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s; %(levelname)s; %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

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
    """Проверка токенов."""
    for name, element in {
        'Токен практикума': PRACTICUM_TOKEN,
        'Токен телеграма': TELEGRAM_TOKEN,
        'ID чата': TELEGRAM_CHAT_ID,
    }.items():
        if element is None:
            logger.critical(
                f'Отсутствует обязательная переменная окружения {name}'
            )
            raise TokenNotFound(
                f'Отсутствует обязательная переменная окружения {name}'
            )


def send_message(bot, message):
    """Отправка сообщений."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение успешно отправлено')
    except Exception as error:
        logger.error(f'Cообщение не отправлено {error}')


def get_api_answer(timestamp):
    """Получение ответа от API."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != 200:
            raise requests.RequestException(
                f'API вернул код {response.status_code}'
            )
    except Exception as error:
        raise Exception(f'Ошибка {error}')
    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    if type(response) is not dict:
        logger.error('Неожиданный тип данных')
        raise TypeError('Неожиданный тип данных')
    homeworks = response.get('homeworks')
    if type(homeworks) is not list:
        logger.error('Неожиданный тип данных')
        raise TypeError('Неожиданный тип данных')
    if homeworks == []:
        raise HomeworkNotFound('Отсутствует обновление статуса')
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
            logger.error(f'Отсутсвует {name}')
            raise KeyError(f'Отсутсвует {name}')
    if status not in HOMEWORK_VERDICTS:
        logger.error('Неожиданный статус домашней работы')
        raise ValueError('Неожиданный статус домашней работы')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:

        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)

        except HomeworkNotFound:
            logger.debug('Отсутствует обновление статуса')

        except Exception as error:
            logger.error(f'Ошибка при запросе к основному API: {error}')
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
