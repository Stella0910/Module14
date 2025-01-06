import sqlite3

connection_products = sqlite3.connect('Products.db')
cursor_products = connection_products.cursor()

connection_users = sqlite3.connect('Users.db')
cursor_users = connection_users.cursor()


def initiate_db():
    cursor_products.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL)
    ''')
    connection_products.commit()

    cursor_users.execute('''
        CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL)
        ''')
    connection_users.commit()


def is_included_product(title):
    initiate_db()
    check_product = cursor_products.execute('SELECT * FROM Products WHERE title = ?', (title,))
    if check_product.fetchone() is not None:
        return True
    else:
        return False


def add_product(title, description, price):
    initiate_db()
    cursor_products.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
                            (f"{title}", f"{description}", f"{price}"))
    connection_products.commit()


def add_user(username, email, age):
    initiate_db()
    cursor_users.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
                         (f"{username}", f"{email}", f"{age}", 1000))
    connection_users.commit()


def is_included(username):
    initiate_db()
    check_user = cursor_users.execute('SELECT * FROM Users WHERE username = ?', (username,))
    if check_user.fetchone() is not None:
        return True
    else:
        return False


def get_all_products():
    initiate_db()
    cursor_products.execute('SELECT * FROM Products')
    result = cursor_products.fetchall()
    return result
