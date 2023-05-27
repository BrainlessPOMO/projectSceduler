from os.path import exists
import sqlite3
from sqlite3 import Error

db_name = r"projects.db"


def create_connection():
    """ create a database connection to a SQLite database """
    try:
        global conn
        conn = sqlite3.connect(db_name)

        global cursor
        cursor = conn.cursor()
    except Error as e:
        print(e)


def close_connection():
    if conn:
        conn.close()


def create_tables():
    create_connection()
    query = """CREATE TABLE if not exists project(
          id INTEGER PRIMARY KEY,
          class_name TEXT,
          until_date text,
          progress INTEGER(100)
          )"""
    cursor.execute(query)
    conn.commit()
    close_connection()


def delete_tables():
    query = """DROP TABLE project"""
    cursor.execute(query)
    conn.commit()


def insert(name, date, progress):
    create_connection()

    query = f"""insert into project (class_name, until_date, progress) 
            values ("{name}", {date}, {progress})"""

    cursor.execute(query)
    conn.commit()
    close_connection()


def insert_test():
    create_connection()
    query = """insert into project (class_name, until_date, progress) values 
            ("test class", "2023-06-26", 0),
            ("eΕπιχειρείν", "2023-05-30", 20),
            ("Διάχυτος Υπολογισμός", "2023-06-14", 40),
            ("Εξόρυξη Δεδομένων και Αλγόριθμοι Μάθησης", "2023-07-27", 60),
            ("test class 5", "2024-05-26", 80),
            ("test class 6", "2023-08-20", 100),
            ("test class 7", "2023-03-26", 15),
            ("test class 8", "2023-02-26", 36),
            ("test class 9", "2023-10-26", 78),
            ("test class 10", "2023-11-26", 49),
            ("test class 11", "2023-12-26", 57)"""
    cursor.execute(query)
    conn.commit()
    close_connection()


def update_item(item_id, item_name, item_date, item_progress):
    create_connection()
    query = f"""update project 
                set class_name = '{item_name}', until_date = '{item_date}', progress = {item_progress} 
                where id = {item_id}"""
    cursor.execute(query)
    conn.commit()
    close_connection()


def add_item(item_name, item_date, item_progress):
    create_connection()
    query = f"""insert into project (class_name, until_date, progress) values 
            ("{item_name}", "{item_date}", {item_progress})"""
    cursor.execute(query)
    conn.commit()
    close_connection()


def delete_item(item_id):
    create_connection()
    query = f"""delete from project where id = {item_id}"""
    cursor.execute(query)
    conn.commit()
    close_connection()


def get_data():
    create_connection()
    rows = cursor.execute("""select * from project""").fetchall()
    close_connection()

    return rows


def repair_database():
    create_connection()
    delete_tables()
    create_tables()
    close_connection()


def first_setup():
    create_connection()
    create_tables()
    close_connection()


if __name__ == "__main__":
    create_tables()

    rows = get_data()

    for row in rows:
        print(
            f"id: {row[0]}\nclass_name: {row[1]}\nuntil_date: {row[2]}\nprogress: {row[3]}\n")
