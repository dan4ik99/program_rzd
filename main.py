import eel
import pandas as pd
import itertools
import networkx as nx
import numpy.random as rnd
import matplotlib.pyplot as plt
from pretty_html_table import build_table
import matplotlib.pyplot as plt
import traceback


class Path:
    def __init__(self, a_point, b_point):
        self.a_point = a_point
        self.b_point = b_point
        self.way_type = 'optimal'
        self.delete_node = None

    def find_way(self):
        oct = pd.read_csv('oct.csv', sep=';')
        oct['point_A'] = oct['point_A'].str.lower()
        oct['point_B'] = oct['point_B'].str.lower()
        u_a = set(oct['point_A'].unique())
        u_b = set(oct['point_B'].unique())
        list_st = list(u_a | u_b)  # Уникальный список станций Октябрьской Ж/Д

        g = nx.Graph()

        edgelist = []
        for i in range(len(oct['point_A'])):
            edgelist.append([oct['point_A'][i], oct['point_B'][i], oct['distance'][i]])

        #Дополнительная логика для случая, когда удаляется одна из вершин графа для перестроения оптимального маршрута
        if self.way_type == 'optimal_with_delete_node':
            edge_list_copy = edgelist.copy()
            edgelist.clear()
            for i in range(len(edge_list_copy)):
                if edge_list_copy[i][0] != str(self.delete_node) and edge_list_copy[i][1] != str(self.delete_node):
                    edgelist.append(edge_list_copy[i])

        for edge in edgelist:
            g.add_edge(edge[0], edge[1], weight=edge[2])

        if self.a_point.lower() not in list_st or self.b_point.lower() not in list_st:
            return 'Введены некорректные данные. Проверьте правильность написания и повторите попытку.'
        elif (nx.has_path(g, self.a_point, self.b_point) == False) and \
             (self.way_type == 'optimal_with_delete_node'):
            return 'Альтернативный проезд через убранную станцию отсутствует. Маршрут не может быть построен. Введите другую станцию и рассчитайте заново'

        path = nx.shortest_path(g, self.a_point, self.b_point, weight='weight')  # Путь
        length = nx.shortest_path_length(g, self.a_point, self.b_point, weight='weight')  # Длина пути

        path_2 = nx.shortest_path(g, self.a_point, self.b_point, weight='weight')
        path_2 = path_2[1:len(path_2)]

        #
        data = []
        for j in range(len(path_2)):
            data.append([path[j], path_2[j]])

        for n in range(len(edgelist)):
            for k in range(len(data)):
                if data[k][0] in edgelist[n] and data[k][1] in edgelist[n]:
                    data[k].append(str(edgelist[n][2]))

        a = []
        b = []
        result = []
        for i in range(len(data)):
            a.append(data[i][0])
            b.append(data[i][1])
            result.append(data[i][2])
        df = pd.DataFrame({'Промежуточная станция A': a, 'Промежуточная станция B': b, 'Расстояние': result})
        table = build_table(df, 'blue_light')
        if self.way_type == 'optimal':
            return table, 'Оптимальный маршрут: ' + str(length) + ' км.'
        elif self.way_type == 'optimal_with_delete_node':
            return table, 'Перестроенный оптимальный маршрут: ' + str(length) + ' км.'

# Оптимальный путь. Функция вызывается из main.html
@eel.expose
def input_data(a_point, b_point):
    optimal_way = Path(a_point, b_point)
    return optimal_way.find_way()

# Оптимальный путь c удалением какой-нибудь станций из графа. Функция вызывается из main.html
@eel.expose
def delete_s(station, a_point, b_point):
    optimal_way_with_delete_node = Path(a_point, b_point)
    optimal_way_with_delete_node.delete_node = station
    optimal_way_with_delete_node.way_type = 'optimal_with_delete_node'
    return optimal_way_with_delete_node.find_way()

eel.init(r'C:\Users\miste\Desktop\program\web')
eel.start('main.html')