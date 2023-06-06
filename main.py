import sqlite3, psutil, time, threading
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta

"""
Создаем экземпляр класса Flask.

Используем декоратор route(), чтобы сказать Flask, какой из url должен запускать нашу функцию.

Создаем соединение с базой данных и таблицу, подключение может использовать несколько потоков.
Создаем 2 таблицы (величина загрузки процессора каждые 5 сек и средняя величина загрузки 
процессора за 1 мин), если они не существует.

Создаем 2 бесконечных цикла. В первом находим загрузку ЦП через каждые 5 сек и добавляем в cpu_load,
Во втором выбираем средние значения загрузки ЦП за 1 минуту и добавляем в average_cpu.

Делаем выборку записей из таблицы cpu_load за последний час и сортируем по id.
Создаем список кортежей из дат и значений ЦП.
После создаем 2 пустых списка для дат и значений ЦП, которые скоро будем наполнять.
Итерируемся по списку кортежей и выделяем первым элементом дату/время, вторым значение ЦП.
Добавляем элементы дата/время и значения ЦП в соответствующие списки.
Сохраняем значения дата/время и ЦП в виде словаря.
Формируем словарь в формат json.

Делаем выборку записей из таблицы cpu_average за последний час и сортируем по id.
Создаем список кортежей из дат и значений ЦП.
После создаем 2 пустых списка для дат и значений ЦП, которые скоро будем наполнять.
Итерируемся по списку кортежей и выделяем первым элементом дату/время, вторым значение ЦП.
Добавляем элементы дата/время и значения ЦП в соответствующие списки.
Сохраняем значения дата/время и ЦП в виде словаря.
Проходимся по всем временным значениям, если это 1е значение, то добавляем его в список вместе 
с соответствующим значением ЦП, если нет, то находим разницу между текущим значением времени и предыдущим.
Если разница > 65 секунд, то ставим пропуск в график.
Возвращаем время/дату и значение ЦП в словарь.
Формируем словарь в формат json.

Запускаем локальный сервер http://127.0.0.1:5000 при помощи функции app.run()
Используем конструкцию if __name__ == '__main__', тк мы запускаем сервис локально их модуля main.py
Вызываем 2 потока для графиков моментальной и средней загрузки ЦП.
"""

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/momental-cpu-data')
def dict1():
    return load_cpu_json()

@app.route('/average-cpu-data')
def dict2():
    return average_cpu_json()


con = sqlite3.connect('data.db', timeout=5, check_same_thread=False)
cursor = con.cursor()
cursor.execute('''
                CREATE TABLE IF NOT EXISTS cpu_load
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample DATETIME,
                load INT)
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS cpu_average
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample DATETIME,
                average INT)
                ''')
con.commit()


def add_load_cpu():
    while True:
        measuring_now = datetime.now()
        load_cpu = psutil.cpu_percent(interval=5)
        cursor.execute('''
                        INSERT INTO cpu_load(sample, load)
                        VALUES(?, ?)
                        ''',
                        (measuring_now, load_cpu))
        con.commit()


def add_average_cpu():
    while True:
        cursor.execute('''
                        SELECT AVG(load)
                        FROM cpu_load
                        WHERE sample >= datetime('now', '-1 minute')
                        ''')
        measuring_now = datetime.now()
        ave_cpu = round(cursor.fetchone()[-1], 2)
        cursor.execute('''
                        INSERT INTO cpu_average(sample, average)
                        VALUES(?, ?)
                        ''',
                        (measuring_now, ave_cpu))
        con.commit()
        time.sleep(60)


def load_cpu_json():
    cursor.execute('''
                    SELECT sample, load
                    FROM cpu_load
                    WHERE sample >= datetime('now', '-60 minute')
                    ORDER BY id
                    ''')
    rows = list(cursor.fetchall())
    timings = []
    cpu_values = []
    for row in rows:
        timing = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        cpu_load = row[1]
        if timings and (timing - timings[-1]) > timedelta(seconds=6):
            for i in range(int((timing - timings[-1]).total_seconds() / 5) - 1):
                timings.append(timings[-1] + timedelta(seconds=5))
                cpu_values.append(None)
        timings.append(timing)
        cpu_values.append(cpu_load)
    dict1 = {'a': timings, 'b': cpu_values}
    return jsonify(dict1)


def average_cpu_json():
    cursor.execute('''
                    SELECT sample, average
                    FROM cpu_average
                    WHERE sample >= datetime('now', '-60 minute')
                    ORDER BY id
                    ''')
    rows = list(cursor.fetchall())
    timings = []
    cpu_values = []
    for row in rows:
        timing = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        cpu_load = row[1]
        timings.append(timing)
        cpu_values.append(cpu_load)
    dict2 = {'c': [],'d': []}
    for i, timing in enumerate(timings):
        if i == 0:
            dict2['c'].append(timing.isoformat())
            dict2['d'].append(cpu_values[i])
        else:
            prev_timing = timings[i - 1]
            diff = timing - prev_timing
            if diff > timedelta(seconds=65):
                clearance = {
                            'c': [prev_timing.isoformat(), timing.isoformat()],
                            'd': [None, None]
                            }
                dict2['c'].extend(clearance['c'])
                dict2['d'].extend(clearance['d'])
            dict2['c'].append(timing.isoformat())
            dict2['d'].append(cpu_values[i])
    return jsonify(dict2)


if __name__ == '__main__':
    thread_add_load_cpu = threading.Thread(target=add_load_cpu)
    thread_add_load_cpu.daemon = True
    thread_add_load_cpu.start()
    
    thread_add_average_cpu = threading.Thread(target=add_average_cpu)
    thread_add_average_cpu.daemon = True
    thread_add_average_cpu.start()

    app.run()