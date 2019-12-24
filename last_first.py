"""""Функция возврата первой или последней буквы слова """""
def last(word):
    if word[-1] == ('ь') or word[-1] == ('ъ') or word[-1] == ('ё') or word[-1] == ('ы'):
        return word[-2]
    else:
        return word[-1]

def first(word):
    return word[0]