import sys 
import requests
from trello import TrelloApi   

base_url = "https://api.trello.com/1/{}" 
auth_params = {    
    'key': "24bc4376d1e16ea2d4e35aacce49a1e2",    
    'token': "750808682d23d004027cfd0ab952cebb8b3b09921cac465978d4c6cd0e6996fc", 
}
board_id = "5dc43f291d182b32bdaa7f8b" 

    
def read():        
    # Получим данные всех колонок на доске:      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()    
      
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:      
    for column in column_data:      
        # Получим данные всех задач в колонке и перечислим все названия      
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print("{} ({})".format(column['name'], len(task_data)))          
        if not task_data:      
            print('\t' + 'Нет задач!')      
            continue      
        for task in task_data:      
            print('\t' + task['name'])    
 
def check_duplicate_task(name, column, i = None):
    # Получим данные всех задач в колонке 
    task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
    # Добавим индекс при совпадении названий задач
    # Повторяем цикл замены, пока есть дубликаты:
    for task in task_data:
        if task["name"] == name:
            if name.find('.copy') == -1:
                name = "{}.{}".format(name, "copy")
            else:
                if name.split('.copy')[1]:
                    i = int(name.split('.copy')[1]) + 1
                else:
                    i = 1
                name = "{}.copy{}".format(name.split('.copy')[0], i)
            name = check_duplicate_task(name, column, i)
    return name

def create_task(name, column_name):      
    # Получим данные всех колонок на доске      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна      
    for column in column_data:
        if column['name'] == column_name:        
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': check_duplicate_task(name, column), 'idList': column['id'], **auth_params})      
    	    # break  

def create_column(name):      
    # Создадим колонку с названием name в таблице с id = board_id       
    requests.post(base_url.format('lists'), data={'name': name , 'idBoard': board_id, **auth_params})
    
def move(name, column_name):    
    # Получим данные всех колонок на доске    
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()    
        
    # Среди всех колонок нужно найти задачу по имени и получить её id    
    task_id = None
    task_list = []
    task_doublicate_index = None    
    for column in column_data:    
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()    
        for task in column_tasks:    
            if task['name'] == name:    
                task_list.append(task)      
    for i, task in enumerate(task_list):
        for column in column_data:
            if(task['idList'] == column['id']):
                print("{}. Задача: {}; Колонка: {}.".format(i, task['name'], column['name']))
    task_doublicate_index = int(input("Введите индекс задачи для ее выбора: "))
    task_id = task_list[task_doublicate_index]['id']
    # Теперь, когда у нас есть id задачи, которую мы хотим переместить    
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу    
    for column in column_data:    
        if column['name'] == column_name:
            # Обновляем данные карточки, если есть совпадение имен, форматируем имя
            requests.put(base_url.format('cards') + '/' + task_id + '/name', 
            data={'value': check_duplicate_task(name, column), **auth_params})    
            # И выполним запрос к API для перемещения задачи в нужную колонку       
            requests.put(base_url.format('cards') + '/' + task_id + '/idList', 
            data={'value': column['id'], **auth_params})    
            break    
    
if __name__ == "__main__":    
    if len(sys.argv) <= 2:    
        read()    
    elif sys.argv[1] == 'create_task':    
        create_task(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':    
        create_column(sys.argv[2])    
    elif sys.argv[1] == 'move':    
        move(sys.argv[2], sys.argv[3])  