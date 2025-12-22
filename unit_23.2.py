import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# user_id = 'Arlett'

def search_all_items_in_tags(tags):
    """
    Функция для поиска всех строк с повторяющимся тегом.
                Например: если у книги несколько авторов или указано несколько жанров.

    :param tags: Повторяющийся тег.
                Например: повторяющийся тег для указания автора книги
                book_author_data = entry.find_all('a', class_='brow-book-author')
    :return q: Список всех строк в повторяющихся тегах.
                Если у книги нет повторений в тегах, в списке будет один элемент.
    """
    q=[]
    for item in tags:
        tag = str(item)
        start_index = tag.find(">")+1
        end_index = tag.find("</a>")
        q.append(replace_to_space(tag[start_index:end_index]))
    return q

def replace_to_space(string):
    """
    Функция для замены неразрывного пробела "\xa0в\xa0" на обычный пробел " ".
            В некоторых получаемых строках (непример, в жанрах книг) могут встречаться "\xa0в\xa0".
            Поэтому возникла необходимость в подобной функции.

    :param string: Строка, в которой ищется "\xa0в\xa0".
    :return q: Строка, с заменёнными обычными пробелами.
    """
    non_space = "\xa0в\xa0"
    if string.find(non_space):
        q = string.replace(non_space," ")
    return q

def collect_user_rates(user_id):
    """
    Функция для парсинга информации о прочитанных книгах пользователя сайта LiveLib.ru.

    :param user_id: Имя пользователя сайта.
    :return data: Список всех прочитанных пользователем книг в виде словарей.
            Вид каждого словаря:
            {'book_name': название_книги, 'book_author': список_авторов,
            'book_genres': список_жанров, 'book_rating': пользовательская_оценка_книги}
    """
    page_num = 1
    data=[]

    while True:
        url=f'https://www.livelib.ru/reader/{user_id}/read/~{page_num}'
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, 'lxml')
        entries = soup.find_all('div', class_='book-item-manage')

        if len(entries) == 0:  # Признак остановки
            break

        for entry in entries:
            book_name = entry.find('a', class_='brow-book-name with-cycle').text
            book_author_data = entry.find_all('a', class_='brow-book-author')
            book_author = search_all_items_in_tags(book_author_data)
            book_genre_data = entry.find_all('a', class_='label-genre')
            book_genre = search_all_items_in_tags(book_genre_data)
            book_rating = entry.find('span', class_='rating-value').text
            data.append({'book_name': book_name, 'book_author': book_author, 'book_genres': book_genre, 'book_rating': book_rating})

        page_num += 1

        # Таймер введён, потому что при частом обращении к сайту парсинг выдаёт нулевые результаты.
        # Для продолжения парсинга или при большом количестве страниц прочитанных книг необходимо ждать.
        time.sleep(1)
    return data

# Вызов функции парсинга информации о прочитанных книгах для пользователя Arlett.
user_rates=collect_user_rates('Arlett')
# Вывод общего количества книг.
# На 29 октября 2025 года - для пользователя Arlett их количество - 926 шт (47 страниц на сайте).
print(len(user_rates))

# Запись полученной информации в файл таблицы excel.
df = pd.DataFrame(user_rates)
df.to_excel('user_book_rates.xlsx')
