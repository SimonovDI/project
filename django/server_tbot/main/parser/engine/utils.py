import time
import requests
import re
from loguru import logger
from bs4 import BeautifulSoup


@logger.catch()
def get_content(url):

    """ Проверка ссылки на код статус и переподключение"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/39.0.2171.95 Safari/537.36'}

    for _ in range(3):
        logger.debug(f"{url} utils.get_content проверка ")
        try:
            content = requests.get(url, headers=headers)
            if content.status_code != 200:
                logger.debug(f"{url} time.sleep(5)")
                time.sleep(5)
            else:
                get_html = BeautifulSoup(content.text, 'lxml')
                logger.debug(f"{url} return: status_code 200")
                return get_html
        except Exception as exc:
            raise Exception(f"Error: {exc} - utils.get_content")


def clear_link(url):
    """валидация url ссылок
    :param url: функция category_links_parsing, функция parse_product
    :return: стандартный формат ссылки https://www.medra.ru/catalog/hvojnye/index.html?p=1
    """
    try:
        deleted_bracket = r'[\(\)]'
        normal_link = re.sub(deleted_bracket, '', url).replace(' ', '')
        return normal_link
    except Exception as exc:
        raise Exception(f"Error: {exc}")
