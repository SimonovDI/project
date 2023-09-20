import os
from dotenv import load_dotenv
from loguru import logger
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from connect_to_base import connect_base, database_query
from utils import check_empy_list, check_card, pagination


logger.add("log\\logging_bot.log", format="{time} {level} {message}", level='DEBUG', rotation='15 MB',
           retention="1 Days")
load_dotenv()

bot = Bot(os.getenv('TELEGRAM_API_ID'))
dp = Dispatcher(bot)


async def on_startup(__):
    """
    Print для отображения состояния бота
    """

    print('Бот запущен')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Обработка команды start
    :param message: Сообщение пользователя
    :return: Приветствие пользователю и примеры работы с ботом.
    """
    txt = f'Привет, {message.from_user.first_name}! Я - бот по поиску растений в питомниках. Для работы с ботом ' \
          f'напишите название или сорт растения. <b><i>Пример: "Туя", "Мята" или "Брабанд", "Лемон"</i></b>.'

    await bot.send_message(message.from_user.id, text=txt, parse_mode='html')
    await message.delete()


@dp.message_handler()
async def message_user(message: types.Message):
    """
    Обработка сообщений от пользователя.
    :param message: Сообщение от пользователя.
    :return: список кнопок 10 шт. + кнопка <<< Показать еще товар ... >>> (если нужно)
    """

    try:
        page_number = 10  # 1 страница, счет страниц начинается с 10
        keyboard = InlineKeyboardMarkup(row_width=1)
        cursor = connect_base()
        up_register_name = message.text.upper()  # имя в верхнем регистре для поиска в БД
        list_product = database_query(cursor, up_register_name)  # запрос в БД
        valid_list = check_empy_list(list_product)  # проверка на пустой список
        lst_button = pagination(valid_list, page=0)
        next_page = f'next_{up_register_name}_{page_number}'  # формирование следующих 10 кнопок + запрос пользователя

        # В условии if проходит проверка на вывод кнопок - 10 шт

        if len(lst_button) != 0:
            if len(lst_button) < 9:
                keyboard.add(*lst_button)
                await bot.send_message(message.from_user.id, 'По Вашему запросу в базе нашлось', reply_markup=keyboard)
            if len(lst_button) >= 10:
                btn_next = InlineKeyboardButton(text='Показать еще товар ...', callback_data=next_page)
                keyboard.add(*lst_button).add(btn_next)
                await bot.send_message(message.from_user.id, 'По Вашему запросу в базе нашлось', reply_markup=keyboard)

        else:
            await bot.send_message(message.from_user.id, f'В моей базе данных нет растения с названием <b>'
                                                         f'{message.text}</b>', parse_mode='html')
    except Exception as ex:
        logger.debug(f'Error: {ex} - Общий Exception message: ')


@dp.callback_query_handler()
async def inline(call: types.CallbackQuery):
    """
    Обработка callback.
    :param call: Нажатая кнопка товара или кнопка <<< Посмотреть еще ... >>>
    :return: следующую страницу (если она есть) или карточку товара
    """

    try:
        item_position = call.data.split('_')  # нажата кнопка next или выбрана карточка товара
        next_btn = item_position[0]
        if next_btn == 'next':
            try:
                keyboard = InlineKeyboardMarkup(row_width=1)
                page = int(item_position[2])
                cursor = connect_base()
                up_register_name = item_position[1].upper()
                list_product = database_query(cursor, up_register_name)
                valid_list = check_empy_list(list_product)
                lst_button = pagination(valid_list, page=page)
                product_page_pagination = int(item_position[2]) + 10  # формирование следующей страницы
                next_page = f'next_{up_register_name}_{product_page_pagination}'

                # в условии if проходит проверка на вывод кнопок 10 шт

                if len(lst_button) != 0:
                    if len(lst_button) == 10:
                        btn_next = InlineKeyboardButton(text='Показать еще товар ...', callback_data=next_page)
                        keyboard.add(*lst_button).row(btn_next)
                        await bot.send_message(call.from_user.id, 'По Вашему запросу в базе нашлось',
                                               reply_markup=keyboard)
                        await call.answer()
                        await call.message.delete()
                    if len(lst_button) < 10:
                        keyboard.add(*lst_button)
                        await bot.send_message(call.from_user.id, 'По Вашему запросу в базе нашлось',
                                               reply_markup=keyboard)
                        await call.answer()
                        await call.message.delete()
            except Exception as exc:
                logger.debug(f'Error: {exc} - обработчик запросов call, блок name = next')

        # если нажата кнопка товара

        if next_btn != 'next':
            try:
                product_button = call.data
                for item in call.message.reply_markup.inline_keyboard:
                    for item_text in item:
                        if item_text.callback_data == product_button:
                            item_name = None  # для вывода сообщения пользователю в блоке except
                            try:
                                item_name = item_text.text
                                cursor = connect_base()
                                up_name = item_name.upper()
                                cursor.execute(
                                    f'SELECT name,price,description, link FROM main_product WHERE up_name like'
                                    f' \'{up_name}%\'or up_name like \'%{up_name}%\' '
                                    f'or up_name like \'%{up_name}\'')
                                card_data = cursor.fetchall()
                                data_item = check_card(card_data, up_name)
                                name = data_item[0]
                                price = data_item[1]
                                desc = data_item[2]
                                link = data_item[3]

                                # формирование карточки для сообщения пользователю

                                txt = f"<b>Название:</b><i> {name}</i>\n<b>Цена:</b> {price}\n<b>Описание:</b> {desc}"
                                btn_link = InlineKeyboardMarkup(row_width=1)
                                btn = InlineKeyboardButton(text='Ссылка', url=link)
                                btn_link.add(btn)
                                await bot.send_message(call.from_user.id, txt, reply_markup=btn_link, parse_mode='html')
                                await call.answer()
                            except Exception as exc:
                                logger.debug(f'Error: {exc} - callback блок name != next ошибка заполнения карточки')
                                error_txt = f'<b><i>К сожалению, по выбранному товару {item_name} нет информации</i></b>'
                                await bot.send_message(call.from_user.id, text=error_txt, parse_mode='html')
            except Exception as ex:
                logger.debug(f'Error: {ex} - callback блок name != next')
    except Exception as ex:
        raise Exception(f'Error: {ex} - Общий Exception call: types.CallbackQuery ')


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
