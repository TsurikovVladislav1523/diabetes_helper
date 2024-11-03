import sqlite3


def create_tables():
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id TEXT UNIQUE,
            gender TEXT,
            height REAL,
            weight REAL,
            age INTEGER
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            time TEXT,
            name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sugar_level REAL,
            image_id TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            type TEXT,
            eat TEXT,
            xe INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        conn.commit()


# Функции для работы с пользователями
def create_user(tg_id, gender, height, weight, age):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (tg_id, gender, height, weight, age)
        VALUES (?, ?, ?, ?, ?)
        ''', (tg_id, gender, height, weight, age))
        conn.commit()


def edit_user(tg_id, gender=None, height=None, weight=None, age=None):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        updates = []
        if gender is not None:
            updates.append(f"gender = '{gender}'")
        if height is not None:
            updates.append(f"height = {height}")
        if weight is not None:
            updates.append(f"weight = {weight}")
        if age is not None:
            updates.append(f"age = {age}")

        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE tg_id = ?"
            cursor.execute(query, (tg_id,))
            conn.commit()


# def delete_user(tg_id):
#     with sqlite3.connect('diabetes_tracker.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('DELETE FROM users WHERE tg_id = ?', (tg_id,))
#         conn.commit()


def get_user(tg_id):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,))
        return cursor.fetchone()


def add_measurement(tg_id, image_id, date, sugar_level=None):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('''
            INSERT INTO measurement (user_id, sugar_level, image_id, date)
            VALUES (?, ?, ?, ?)
            ''', (user[0], sugar_level, image_id, date))
            conn.commit()


def add_eat(tg_id, name, type, eat, xe):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('''
            INSERT INTO menu (user_id, name, type, eat, xe)
            VALUES (?, ?, ?, ?, ?)
            ''', (user[0], name, type, eat, xe))
            conn.commit()



def delete_measurement(tg_id):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('DELETE FROM measurement WHERE user_id = ?', (user[0],))
            conn.commit()


def get_measurement(tg_id):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('SELECT * FROM measurement WHERE user_id = ?', (user[0],))
            return cursor.fetchall()
    return []


# Функции для работы с записями времени
def add_time(tg_id, time, name):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('''
            INSERT INTO times (user_id, time, name)
            VALUES (?, ?, ?)
            ''', (user[0], time, name))
            conn.commit()


# def delete_times(tg_id):
#     with sqlite3.connect('diabetes_tracker.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
#         user = cursor.fetchone()
#         if user:
#             cursor.execute('DELETE FROM times WHERE user_id = ?', (user[0],))
#             conn.commit()


def get_times(tg_id):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute('SELECT * FROM times WHERE user_id = ?', (user[0],))
            return cursor.fetchall()
    return []


def get_times_with_tg_id():
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT users.tg_id, times.time, times.name 
            FROM times 
            JOIN users ON times.user_id = users.id
        ''')

        results = cursor.fetchall()

        formatted_results = [[tg_id, time, name] for tg_id, time, name in results]

    return formatted_results


def get_all_users():
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT tg_id FROM users')
        result = cursor.fetchone()
        if result:
            formatted_results = [int(tg_id) for tg_id in result]
            return formatted_results
        else:
            return []


def update_user_h(tg_id, n_par):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET height = ? WHERE tg_id = ?', (n_par, tg_id,))
        conn.commit()


def update_user_w(tg_id, n_par):
    with sqlite3.connect('diabetes_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET weight = ? WHERE tg_id = ?', (n_par, tg_id,))
        conn.commit()


create_tables()

if __name__ == '__main__':
    # Создание пользователя
    create_user('12345', 'male', 180, 75, 30)

    # Получение информации о пользователе
    print(get_user('12345'))

    # Добавление времени
    add_time('12345', '2024-10-12 10:00:00')

    # Получение всех записей времени
    print(get_times('12345'))

    # Добавление изображения
    add_image('12345', 5.2, 'image_001')

    # Получение всех изображений
    print(get_measurement('12345'))

    # Редактирование пользователя
    edit_user('12345', weight=80)

    # Удаление изображений
    delete_measurement('12345')

    # # Удаление пользователя
    # delete_user('12345')
