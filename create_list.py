import sorting as s
import vectors as v


def create_list():
    v.deleted.clear()
    for i in v.all_alph:
        i.clear()
    file = open(r"CitiesHard.txt").read()  # Открытие файла со списком городов на чтение
    new = file.split("\n")  # Создание вектора всех городов
    s.sort(new)  # Сортировка вектора