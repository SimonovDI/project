import requests
import time
import sys
from .utils import get_content,clear_link
from .parser_contract import ParserContract
from loguru import logger
sys.path.append('..')


class ParserHtml(ParserContract):
    """ Парсинг сайта 'https://www.medra.ru',
    :param url: www.medra.ru
    :return: list[dict{'name': name, 'price': price, 'quantity': quantity, 'links': link_card}]
    """

    def __init__(self, url):
        self._url = url
        self._product_data = []  # описание товара
        self._main_links = []  # ссылки категорий товара
        self._main_url = 'https://www.medra.ru'

    def download_link(self):

        """ Проверка get - запроса на ошибки от главной страницы 'https://www.medra.ru',
        :return: код 200 или Code error URL
        """

        get_html = get_content(self._url)  # utils.py
        return get_html

    @logger.catch()
    def parse_main_links(self):

        """ Парсинг ссылок категорий,
         :param: получение данных от функции download_link
         :return: 8 ссылок с категориями товара в формате list()
         """

        try:
            main_page = self.download_link()
            main_links = main_page.select('.catalog-item__link')
            for item in main_links:
                link = item.attrs['href']
                self._main_links.append(f'{self._main_url}{link}')  # формирование ссылки категории товара
            logger.debug(f" ссылки категории товара сформированы")
            return self._main_links[-8:]  # срез, на сайте есть бегущая строка(нужны только ссылки категорий)
        except Exception as exc:
            raise Exception(f"Error: {exc}")

    def parse_category_links(self):

        """ Парсинг ссылок товара в категории,
         :param: Получает данные с функции parse_main_links
         :return: dict{} с ссылками
         """

        last_page = 1  # Последняя страница в категории
        general_list_links = []  # общий список ссылок с 8 категорий товара
        max_page = []  # всего страниц в категории
        total_pages_in_category = []
        page_product = self.parse_main_links()
        for page in page_product:  # проверка ссылки категории на get - запрос
            res = requests.get(page)
            if res.status_code != 200:
                logger.error(f"{page} parse_category_links != 200")
                raise f'Code error URL {page_product}'
            while last_page:  # цикл пагинации по страницам сайта
                if last_page in total_pages_in_category:
                    break
                page_url = f'{page}?p={last_page}'  # формирование url страницы
                normal_link = clear_link(page_url)  # utils.py
                get_html = get_content(normal_link)
                last_page = int(get_html.select_one('.active').text)  # № последней страницы
                max_page.append(page_url)  # всего страниц в категории
                total_pages_in_category.append(last_page)
                last_page += 1

            general_list_links += max_page[:-1]  # формирование единого списка товара
            last_page = 1  # сброс счетчика страниц
            max_page.clear()
            total_pages_in_category.clear()  # очистка данных (нужно для логики)
        logger.debug(f"список ссылок товаров в категории 100%")
        return general_list_links

    @logger.catch()
    def parse(self):

        """ Парсинг информации товара
        :param: получает данные с category_links_parsing
        :return: dict{'name': name, 'price': price, 'quantity': quantity, 'links': normal_link}
        """
        up_name = None
        start = time.time()
        data_cards = self.parse_category_links()
        for info_card in data_cards:  # цикл по карточкам товара, получение данных с них
            logger.debug(f" Итерация в parse.data_cards")
            get_html = get_content(info_card)  # файл utils.py
            card_product = get_html.select('.catalog-item .nom-actions .btn-bigbuy.btn.button')
            for item in card_product:  # цикл внутри карточки товара.
                logger.debug(f" Итерация в parse.card_product")
                try:
                    link = item.attrs['href']
                    link_card = f'{self._main_url}{link}'  # формирование ссылки карточки товара
                    normal_link = clear_link(link_card)  # utils.py валидация ссылки
                    get_html = get_content(normal_link)  # файл utils.py
                    try:
                        name = get_html.select_one('.main h1').text  # получение данных с карточки товара
                        price = get_html.select_one('.price').text
                        description = get_html.select_one('.tabcontent').text
                        up_name = name.upper()
                    except AttributeError:
                        logger.error(f"{normal_link} - ParserHtml.parse.AttributeError")  # log файл
                        name = ' '
                        price = ' '
                        description = ' '
                    remove_spaces = ' '.join(description.split())  # объединение и удаление лишних пробелов
                    product_description = {
                        'name': name,
                        'price': price,
                        'description': remove_spaces,
                        'link': normal_link,
                        'up_name': up_name
                    }
                    self._product_data.append(product_description)
                except requests.exceptions.TooManyRedirects:
                    logger.warning(f"{card_product} - parse.TooManyRedirects")  # log файл
                    logger.info('parse.TooManyRedirects - pass')
                except TimeoutError:
                    logger.warning(f"{card_product} - parse.TimeoutError")
                    logger.debug('time_sleep = 60 sec')
                    time.sleep(60)
                    logger.debug('Переподключение')
                except Exception as ex:
                    logger.error(f'parse общий Exception {ex}')
        end = (time.time() - start) / 60
        logger.debug(f"{end} минут - время формирования словаря product_data")
        return self._product_data
        # dict{'name': name, 'price': price, 'quantity': quantity, 'links': link_card, 'up_name':up_name}


def main():
    parser_html = ParserHtml('https://www.medra.ru/')
    return parser_html


if __name__ == '__main__':
    main()
