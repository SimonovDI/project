from .utils import get_content
from .parser_contract import ParserContract
from loguru import logger


class ParserZaoksky(ParserContract):

    def __init__(self, url):
        self._url = url  # главная ссылка
        self._category = []  # ссылки категории
        self._info_card = []  # описание карточки товара
        self._card_link = []  # ссылка карточки
        self._main_url = 'https://www.zpitomniki.ru'

    def download_link(self):

        """ Проверка get - запроса на ошибки от главной страницы 'https://www.zpitomniki.ru/',
        :return: код 200 или Code error URL
        """

        get_status = get_content(self._url)  # utils.py
        return get_status

    def parse_main_links(self):
        """
        Парсинг главных ссылок.
        :return: [str,str,str]
        """
        try:
            main_page = self.download_link()
            main_links = main_page.select('.js-glide-catalog__nav')
            for item in main_links:
                category = item.find('div')['tabs.link']
                category_link = self._main_url + category
                if category_link not in self._category:
                    self._category.append(category_link)
            return self._category
        except Exception as exc:
            logger.debug(f"{exc} - parse_main_links")
            raise Exception(f"Error: {exc}")

    def parse_category_links(self):
        """
        Парсинг ссылок категории.
        :return: [str,str,str]
        """
        try:
            page_in_category_link = []
            category_url = self.parse_main_links()
            for item in category_url:
                last_page = 1
                while last_page != 0:  # пагинация
                    max_page = f"{item}?PAGEN_1={last_page}"  # формируем ссылку страницы
                    get_html = get_content(max_page)  # файл utils.py
                    check_tag_a = get_html.find('a', class_='ml-5 inline-flex items-center py-2 mr-2 font-semibold leading-loose text-gray-650')
                    try:
                        _ = check_tag_a.get_text(strip=True)  # проверка тега "а", нужно для логики
                        page_in_category_link.append(max_page)
                        last_page += 1
                    except AttributeError:  # если тег "а" отсутствует, конец формирования пагинации.
                        page_in_category_link.append(max_page)
                        last_page = 0
            return page_in_category_link
        except Exception as exc:
            logger.debug(f"{exc} - parse_category_links")
            raise Exception(f"Error: {exc}")

    def parse_product_link(self):
        """
        Парсинг ссылок карточек товара.
        :return: [str,str,str]
        """
        try:
            product_card_data = self.parse_category_links()
            for item in product_card_data:
                get_html = get_content(item)  # файл utils.py
                link_card = get_html.find_all('a',
                                              class_='hover:opacity-80 border border-green-350 duration-200'
                                                     ' font-semibold group-hover:bg-green-350 group-hover:text-white'
                                                     ' px-8 py-2 rounded-full text-green-350 text-lg '
                                                     'text-white transition-colors')
                for item_href in link_card:
                    h_ref = item_href.get('href')
                    self._card_link.append(self._main_url + h_ref)
            return self._card_link
        except Exception as exc:
            logger.debug(f" {exc} - parse_product_link")
            raise Exception(f"Error: {exc}")

    def parse(self):
        """
        Парсинг информации в карточке товара.
        :return: [dict(), dict()]
        """
        try:
            card_link = self.parse_product_link()
            for item in card_link:
                get_html = get_content(item)  # файл utils.py
                try:
                    name = get_html.find('h1',
                                         class_='mb-4 text-2xl font-extrabold leading-none md:text-3xl xl:text-4xl').text
                    price = get_html.find('div', class_='offer__price').text
                    if price == '':
                        price = '0'
                    description = get_html.find('div', itemprop="description").text
                except AttributeError:
                    name = ' '
                    price = ' '
                    description = ' '
                remove_spaces = ' '.join(description.split())  # объединение и удаление лишних пробелов
                product_description = {
                    'name': name,
                    'price': price,
                    'description': 'См. на сайте питомника' if len(remove_spaces) > 1000 else remove_spaces,
                    'link': item,
                    'up_name': name.upper()
                }
                self._info_card.append(product_description)
            return self._info_card
        except Exception as exc:
            logger.debug(f"{exc} - parse")
            raise Exception(f"Error: {exc}")


def main():
    parser = ParserZaoksky('https://www.zpitomniki.ru')
    return parser


if __name__ == '__main__':
    main()
