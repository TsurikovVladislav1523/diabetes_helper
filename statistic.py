import os
from config import TOKEN
from aiogram import Bot
from aiogram.types import FSInputFile
from data_base import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
bot = Bot(token=TOKEN)
def sugar_level(id):
    all_photo = get_measurement(id)
    slovar = {}
    for ph in all_photo:
        date = ph[4]
        if date in slovar:
            slovar[date].append(float(ph[2]))
        else:
            slovar[date] = []
            slovar[date].append(float(ph[2]))
    x = []
    y = []
    for key in slovar:
        sp = slovar[key]
        x.append(key)
        res = round(sum(sp) / len(sp), 1)
        y.append(res)
    # ax = plt.axes()
    # ax.set_facecolor("dimgray")
    plt.title("Среднее значение уровня сахара за каждый из дней")  # заголовок
    plt.xlabel("День")  # ось абсцисс
    plt.ylabel("Уровень сахара")  # ось ординат
    plt.grid(True)  # включение отображение сетки
    plt.minorticks_on()
    plt.plot(x, y, "b--", marker='o', markersize=4)  # построение графика
    plt.savefig(f"images/{id}_sug_1.png")
    graph1 = f"images/{id}_sug_1.png"
    plt.clf()
    plt.minorticks_on()
    plt.bar(x, y, label='Уровень сахара',
            color='skyblue')  # Параметр label позволяет задать название величины для легенды
    plt.xlabel('День')
    plt.ylabel('Уровень сахара')
    plt.title('Среднее значение уровня сахара за каждый из дней')
    plt.legend(loc='lower left')
    for c in range(len(y)):
        plt.annotate(y[c], xy=(c - 0.25, y[c] - 0.5), color='black')
    plt.savefig(f"images/{id}_sug_2.png")
    graph2 = f"images/{id}_sug_2.png"
    plt.clf()
    return [graph1, graph2]

def meal_stats(id):
    all_data = get_meal(id)
    sl = {}
    for data in all_data:
        if data[2] not in sl:
            sl[data[2]] = {}
            sl[data[2]][data[4]] = data[3]
        else:
            if data[4] in sl[data[2]]:
                sl[data[2]][data[4]] += data[3]
            else:
                sl[data[2]][data[4]] = data[3]
    data_coords = {}
    for key in sl:
        data_coords[key] = [[],[]]
        for date in sl[key]:
            data_coords[key][0].append(date)
            data_coords[key][1].append(round(sl[key][date], 2))
    x = []
    y = []
    for data in all_data:
        if data[4] not in x:
            x.append(data[4])
            y.append(round(data[3], 2))
        else:
            y[-1] += round(data[3], 2)
    for i in range(len(y)):
        y[i] = round(y[i], 1)
    graphs = []
    for title in data_coords:
        plt.minorticks_on()
        plt.bar(data_coords[title][0], data_coords[title][1], label=f'Количество потребленных ХЕ. {title}',
                color='skyblue')  # Параметр label позволяет задать название величины для легенды
        plt.xlabel('День')
        plt.ylabel('ХЕ')
        plt.title(f'Количество потребленных ХЕ. {title}')
        plt.legend(loc='lower left')
        for c in range(len(data_coords[title][1])):
            plt.annotate(data_coords[title][1][c], xy=(c - 0.25, data_coords[title][1][c] - 0.5), color='black')
        plt.savefig(f'images/{id}_{title}.png')
        graphs.append(f'images/{id}_{title}.png')
        plt.clf()

    plt.title("Суммарное количество потребленных ХЕ")  # заголовок
    plt.xlabel("День")  # ось абсцисс
    plt.ylabel("ХЕ")  # ось ординат
    plt.minorticks_on()
    plt.plot(x, y, "b--", marker='o', markersize=4)  # построение графика

    plt.minorticks_on()
    plt.bar(x, y, label='ХЕ',
            color='skyblue')  # Параметр label позволяет задать название величины для легенды
    plt.legend(loc='lower left')
    for c in range(len(y)):
        plt.annotate(y[c], xy=(c - 0.25, y[c] - 3), color='black')
    plt.savefig(f'images/{id}_all.png')
    graphs.append(f'images/{id}_all.png')
    plt.clf()
    return graphs


def sugar_level_web(id):
    all_photo = get_measurement(id)
    slovar = {}
    for ph in all_photo:
        date = ph[4]
        if date in slovar:
            slovar[date].append(float(ph[2]))
        else:
            slovar[date] = []
            slovar[date].append(float(ph[2]))
    x = []
    y = []
    for key in slovar:
        sp = slovar[key]
        x.append(key)
        res = round(sum(sp) / len(sp), 1)
        y.append(res)
    # ax = plt.axes()
    # ax.set_facecolor("dimgray")
    plt.title("Среднее значение уровня сахара за каждый из дней")  # заголовок
    plt.xlabel("День")  # ось абсцисс
    plt.ylabel("Уровень сахара")  # ось ординат
    plt.grid(True)  # включение отображение сетки
    plt.minorticks_on()
    plt.plot(x, y, "b--", marker='o', markersize=4)  # построение графика
    plt.savefig(f"static/uploads/{id}_sug_1.jpeg")
    plt.savefig(f"uploads/{id}_sug_1.jpeg")
    graph1 = f"{id}_sug_1.jpeg"
    plt.clf()
    plt.minorticks_on()
    plt.bar(x, y, label='Уровень сахара',
            color='skyblue')  # Параметр label позволяет задать название величины для легенды
    plt.xlabel('День')
    plt.ylabel('Уровень сахара')
    plt.title('Среднее значение уровня сахара за каждый из дней')
    plt.legend(loc='lower left')
    for c in range(len(y)):
        plt.annotate(y[c], xy=(c - 0.25, y[c] - 0.5), color='black')
    plt.savefig(f"static/uploads/{id}_sug_2.jpeg")
    plt.savefig(f"uploads/{id}_sug_2.jpeg")
    graph2 = f"{id}_sug_2.jpeg"
    plt.clf()
    return [graph1, graph2]

def meal_stats_web(id):
    all_data = get_meal(id)
    sl = {}
    for data in all_data:
        if data[2] not in sl:
            sl[data[2]] = {}
            sl[data[2]][data[4]] = data[3]
        else:
            if data[4] in sl[data[2]]:
                sl[data[2]][data[4]] += data[3]
            else:
                sl[data[2]][data[4]] = data[3]
    data_coords = {}
    for key in sl:
        data_coords[key] = [[],[]]
        for date in sl[key]:
            data_coords[key][0].append(date)
            data_coords[key][1].append(round(sl[key][date], 2))
    x = []
    y = []
    for data in all_data:
        if data[4] not in x:
            x.append(data[4])
            y.append(round(data[3], 2))
        else:
            y[-1] += round(data[3], 2)
    for i in range(len(y)):
        y[i] = round(y[i], 1)
    graphs = []
    for title in data_coords:
        plt.minorticks_on()
        plt.bar(data_coords[title][0], data_coords[title][1], label=f'Количество потребленных ХЕ. {title}',
                color='skyblue')  # Параметр label позволяет задать название величины для легенды
        plt.xlabel('День')
        plt.ylabel('ХЕ')
        plt.title(f'Количество потребленных ХЕ. {title}')
        plt.legend(loc='lower left')
        for c in range(len(data_coords[title][1])):
            plt.annotate(data_coords[title][1][c], xy=(c - 0.25, data_coords[title][1][c] - 0.5), color='black')
        plt.savefig(f'static/uploads/{id}_{title}.jpeg')
        plt.savefig(f'uploads/{id}_{title}.jpeg')
        graphs.append(f'{id}_{title}.jpeg')
        plt.clf()

    plt.title("Суммарное количество потребленных ХЕ")  # заголовок
    plt.xlabel("День")  # ось абсцисс
    plt.ylabel("ХЕ")  # ось ординат
    plt.minorticks_on()
    plt.plot(x, y, "b--", marker='o', markersize=4)  # построение графика

    plt.minorticks_on()
    plt.bar(x, y, label='ХЕ',
            color='skyblue')  # Параметр label позволяет задать название величины для легенды
    plt.legend(loc='lower left')
    for c in range(len(y)):
        plt.annotate(y[c], xy=(c - 0.25, y[c] - 3), color='black')
    plt.savefig(f'static/uploads/{id}_all.jpeg')
    plt.savefig(f'uploads/{id}_all.jpeg')
    graphs.append(f'{id}_all.jpeg')
    plt.clf()
    return graphs