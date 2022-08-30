import sqlite3


def sqlite(command, time, hotels):
    connect = sqlite3.connect('database/database.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS data(
        command TEXT NOT NULL, 
        time DATE NOT NULL, 
        hotel TEXT NOT NULL
    );""")

    connect.commit()

    for hotel in hotels:
        information_on_request = (command, time, hotel)
        cursor.execute("INSERT INTO data ( command, time, hotel ) VALUES (?, ?, ?);", information_on_request)
        connect.commit()