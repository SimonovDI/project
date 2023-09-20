from aiogram.types import InlineKeyboardButton


def check_card(card_data, up_message):
    """
    Проверка корректности данных в карточке товара.
    :param card_data: Карточка товара из БД
    :param up_message: имя товара в upper регистре
    :return: Кортеж name, price, description, link
    """

    try:
        if len(card_data) > 0 and up_message != 'ИТОГО':
            for item in card_data:
                name = item[0]
                price = item[1]
                description = item[2]
                link = item[3]
                if name == ' ':
                    name = 'Пустая строка'
                if price == '0 ₽' or price == '0':
                    price = f'Уточняйте у продавца'
                if link in 'https://fittonia.ru':
                    description = f'См. на сайте питомника'
                    return name, price, description, link
                else:
                    return name, price, description, link
    except Exception as ex:
        raise Exception(f'Error: {ex} - Общий Exception utils.check  ')


def check_empy_list(lst_data):
    """
    Проверка списка товара
    :param lst_data: список товара
    :return: пустой список или нет.
    """

    try:
        if len(lst_data) != 0:
            return lst_data if lst_data else []
        return []
    except Exception as ex:
        raise Exception(f'Error: {ex} - Общий Exception  utils.check_empy_list  ')


def pagination(lst_data, page=None):
    """
    Пагинация списка с товаром(10 шт в одном сообщений)
    :param lst_data: Проверенный список товара
    :param page: № страницы
    :return: Кнопки 10 шт
    """
    if lst_data is not None:
        try:
            button_list_page = []
            button_number = 0
            for item in lst_data[page:page + 10]:
                button_number += 1
                name_product = item[0]
                if name_product == ' ':
                    continue
                btn = InlineKeyboardButton(text=name_product, callback_data=str(f'{button_number}_{page + 10}'))
                button_list_page.append(btn)
            return button_list_page
        except Exception as ex:
            raise ex



