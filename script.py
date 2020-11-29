import json
import jsonschema
from jsonschema import validate
import os

# Взято отсюда: https://ru.wikibooks.org/wiki/Реализации_алгоритмов/Расстояние_Левенштейна#Python
def distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]

def find_schema(sch_list, evnt):
    '''
    Находит схему с максимальным соответствием
    '''
    # Сначала избавимся от возможных случайных пробелов, которых точно нет в названии наших схем
    evnt = evnt.replace(' ', '')

    schema = sch_list[0]
    difference = distance(schema[:-7], evnt)
    for sch in sch_list[1:]:
        d = distance(sch[:-7], evnt) 
        if d < difference:
            difference = d
            schema = sch
    return schema

event_files = os.listdir('event')
schema_names = [x[:-7] for x in os.listdir('schema')]

with open('readme.log', 'w', encoding='utf8') as log:
    # Итерируемся по всем событиям
    for event_file in event_files:
        with open(f'.\event\{event_file}', 'r') as file:
            instance = json.load(file)
        
        log.write(f'Файл события: {event_file}\n')
        
        # Cчетчик ошибок
        error_counter = 0

        # Выберем нужную для обработки ошибок схему
        if instance and 'event' in instance.keys():
            if instance['event'] not in schema_names:
                schema = find_schema(schema_names, instance['event']) + '.schema'
                log.write(
                    f"Ошибка: Некорректное имя схемы в событии: " \
                    f"\"{instance['event']}\"\n"
                )
                error_counter += 1
            else:
                schema = instance['event'] + '.schema'
            
            # Считаем схему
            log.write(f'Использумая схема: {schema}\n')
            with open(f'.\schema\{schema}', 'r') as file:
                schema = json.load(file)
            
            # Переберем все ошибки в событии
            v = jsonschema.Draft3Validator(schema)
            for error in v.iter_errors(instance):
                    error_counter += 1
                    log.write(f'    {error_counter}: {error.message}\n')
            log.write(
                f'\n    Всего ошибок: {error_counter}'
                f'{" Файл валиден." if error_counter == 0 else ""}\n'
            )
            log.writelines(['-' * 40, '\n'])

        else:
            error_counter += 1
            log.writelines([
                "Ошибка: В файле события отсутствует назнание схемы\n",
                "или файл не содержит данных, файл обработан не будет.\n",
                f'\n    Всего ошибок: {error_counter}\n',
                '-' * 40,
                '\n'
            ])
