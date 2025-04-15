from pyvis.network import Network
import re
from typing import Any,List,Tuple,NoReturn
import os
import pandas as pd
from traceback import format_exc

def search_files_paths(path):
    return [os.path.join(dp,f) for dp,dn,filenames in os.walk(path) for f in filenames]

def transform_graph_html(
    paths_dict : dict={
        'html_path':'graph.html',
        'utils_path':None,
        'network_js_path':None,
        'network_css_path':None
    }
)->NoReturn:
    """
        Работает с html-файлом графа. Меняет пути библиотек для работы.
        Parameters:
        ----------
        paths_dict : словарь с путями к необходимым библиотекам
    """
    try:
        # проверяем существование указанных файлов библиотек
        exist_files = [os.path.exists(str(file_path)[3:]) for file_path in list(paths_dict.values())[1:]]
        # если все файлы существуют, присваиваем их пути для перезаписи файла:
        if all(exist_files):
            utils_path = paths_dict['utils_path']
            network_js_path = paths_dict['network_js_path']
            network_css_path = paths_dict['network_css_path']
        else:
            # если не указаны файлы расположение библиотек, смотрим, есть ли директория lib
            # и забираем из нее файлы для замены
            if os.path.exists(r'lib'):
                # формирование ссылок к файлам
                libs_paths = search_files_paths(r'lib')
                libs_count = 0
                for lib_path in libs_paths:
                    if 'utils.js' in lib_path:
                        utils_path = re.sub(r'\\','/',lib_path)
                        libs_count+=1
                    elif 'vis-network.min.js' in lib_path:
                        network_js_path = re.sub(r'\\','/',lib_path)
                        libs_count +=1
                    elif 'vis-network.css' in lib_path:
                        network_css_path = re.sub(r'\\','/',lib_path)
                        libs_count+=1
                if libs_count<3:
                    raise Exception('Недостаточно библиотек для работы')
            else:
                raise Exception('Некорректные пути к файлам библиотек')
        # формируем список паттернов для замены
        replace_pattern  = {
            r'<script src="lib/bindings/utils.js"></script>' : f'<script src="{utils_path}"></script>',
            r'<link rel="stylesheet".*vis-network\.min\.css.*/>' : f'<link rel="stylesheet" href="{network_css_path}"/>',
            r'<script src=.*vis-network\.min\.js.*>' : f'<script src="{network_js_path}"></script>',
            r'<link\s*.*bootstrap\.min\.css[.\n\S\s]*\/>' : '',
            r'<script\s*.*bootstrap\.bundle\.min\.js[.\n\S\s]*\><\/script>':''
        }
        with open(paths_dict['html_path'], 'r+', encoding='cp1251') as file:
            text = file.read()
            for key, value in replace_pattern.items():
                text = re.sub(key,value,text)
            file.seek(0)
            file.write(text)
            file.truncate()
    except:
        print(f'В ходе формирования html-файла с графом произошла огибка:\n{format_exc()}')

def create_graph(
    nodes :List[int],
    labels : List[str],
    edges : List[set],
    colors : Any=None,
    filename=r'graph.html'
)->NoReturn:
    """
    Создаёт html-файл с интерактивным графом
    Parameters:
    ----------
    nodes : список вершин графа
    labels : список имен вершин графа
    edges : список рёбер графа
    """
    net = Network()
    net.add_nodes(
        nodes,
        label = labels,
        color = colors
    )
    net.add_edges(edges)
    net.show_buttons(filter_=['physics'])
    net.save_graph(filename)

def search_graph_params(
    df : pd.DataFrame,
    sender_column : str,
    recipient_column : str,
    columns_type : str = 'int'
):
    """
        На основании входного датафрейма формирует необходимые для построения графа параметры.
        Parameters:
        ----------
        df : pandas dataframe с данными
        sender_column : название колонки с отправителями
        recipients : название колонки с получателями
    """
    try:
        nodes,labels,edges,prepare_dictionary = None,None,None,None
        prepare_dictionary = {}
        senders_list = df[sender_column].tolist()
        recipients_list = df[recipient_column].tolist()
        nodes = list(set(senders_list+recipients_list))
        if columns_type=='int':
            labels = [str(node) for node in nodes]
            edges = list(zip(senders_list, recipients_list))
        # для корректной работы с Networkx ноды должны быть int
        elif columns_type=='str':
            nodes_dict = dict(zip(nodes,range(0,len(nodes))))
            prepare_dictionary = dict(zip(range(0,len(nodes)), nodes))
            nodes = list(nodes_dict.values())
            labels = list(nodes_dict.keys())
            # изменяем тип связей вместо ФИО1->ФИО2 на 1->2 и т.д
            edges = []
            for sender, recipient in zip(senders_list, recipients_list):
                edges.append(
                    (nodes_dict[sender], nodes_dict[recipient])
                )
        return nodes, labels, edges, prepare_dictionary
    except:
        print(f'В ходе работы произошла ошибка:\n{format_exc()}')