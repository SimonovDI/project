import xlrd
import requests
from .parser_contract import ParserContract
from loguru import logger


logger.add("log\\logging.log", format="{time} {level} {message}", level='DEBUG', rotation='15 MB',
           retention="1 Days")


class ParserExcel(ParserContract):  #
    """ Загрузка файла Excel с сайта, парсинг файла в ОЗУ
    :param url: https://fittonia.ru/
    :return: dict{'name': name, 'price': price, 'description': description}
        """

    def __init__(self, url):
        self._url = url
        self._lst_data_excel = []

    @logger.catch()
    def parse(self):
        logger.debug('ParserExcel.parse - старт')
        try:
            res = requests.get(self._url)  # get - запрос на скачивание файла
            if res.status_code == 200:
                logger.debug(f"ParserExcel.parse status_code == 200")
                book = xlrd.open_workbook(file_contents=res.content)
                sheet = book.sheet_by_index(0)
                for row in range(7, sheet.nrows):  # выборка данных с файла Excel
                    name = str(sheet.cell(row, 0).value)
                    price = str(sheet.cell(row, 12).value)
                    description = str(sheet.cell(row, 13).value)
                    link = 'https://fittonia.ru'
                    up_name = name.upper()
                    val = {'name': name, 'price': price, 'description': description, 'link': link, 'up_name': up_name}
                    self._lst_data_excel.append(val)
                logger.debug('ParserExcel.parse - загрузка данных - завершено')
                return self._lst_data_excel  # return: dict{'name': name, 'price': price, 'description': description}
            else:
                raise 'Error connect'
        except Exception as exc:
            raise Exception(f"Error: {exc}")


def main():
    parser_excel = ParserExcel('https://fittonia.ru/pricelist/vashutino/')
    return parser_excel


if __name__ == '__main__':
    main()

