import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connect_base():
    """
    Подключение к базе данных.
    :return: cursor
    """
    try:
        connect = psycopg2.connect(dbname=os.getenv('POSTGRES_NAME'),
                                   user=os.getenv('POSTGRES_USER'),
                                   password=os.getenv('POSTGRES_PASSWORD'),
                                   host=os.getenv('POSTGRES_HOST'),
                                   port=os.getenv('POSTGRES_PORT'))
        cursor = connect.cursor()
        return cursor
    except Exception as ex:
        raise ex


def database_query(cursor, up_register_name):
    """
    Запрос в базу данных о наличии товара.
    :param cursor: cursor
    :param up_register_name: Имя товара, в  upper регистре
    :return: товар из БД
    """
    try:
        cursor.execute(f'SELECT name,price,description, link FROM main_product WHERE up_name like '
                       f'\'{up_register_name} %\' or up_name like \'% {up_register_name} %\' '
                       f'or up_name like \'% {up_register_name}\'')
        return cursor.fetchall()
    except Exception as ex:
        raise ex
