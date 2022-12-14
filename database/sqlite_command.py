import sqlite3


def connect_sql() -> sqlite3.Connection:
    """

    Функция необходима для подключения к базе данных SQLite

    """
    with sqlite3.connect('database/database.db') as connect:
        connect.cursor().execute("""CREATE TABLE IF NOT EXISTS data(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                command TEXT NOT NULL, 
                time DATE NOT NULL, 
                hotel TEXT NOT NULL
            );""")

        connect.commit()


def insert_db(command: str, time: str, hotels: str) -> None:
    """
    Функция добавляет новые данные в базу данных.
    Args:
        command: Введенная пользователем команда.
        time: Дата и время, когда команда была введена.
        hotels: Название всех полученных в конце запроса отелей.

    """
    with sqlite3.connect('database/database.db') as connect:
        cursor = connect.cursor()

        for hotel in hotels:
            information_on_request = (command, time, hotel)
            cursor.execute("INSERT INTO data (command, time, hotel ) VALUES (?, ?, ?);", information_on_request)
            connect.commit()
