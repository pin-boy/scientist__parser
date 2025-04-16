import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def clean_text(text):
    """Очищает текст от лишних пробелов и специальных символов"""
    if text:
        # Удаляем ссылки в квадратных скобках
        text = re.sub(r'\[\d+\]', '', text)
        # Удаляем лишние пробелы
        return ' '.join(text.split()).strip()
    return None


def get_person_info(url):
    """Получает информацию о персоне"""
    print(f"\nОбработка страницы: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        person_info = {
            'Дата рождения': None,
            'Место рождения': None,
            'Дата смерти': None,
            'Место смерти': None
        }

        # Находим информационную таблицу
        table = soup.find('table', {'class': 'infobox'})
        if not table:
            print("Не найдена информационная таблица")
            return person_info

        print("\nТаблица найдена, начинаем обработку строк")

        # Перебираем все строки таблицы
        rows = table.find_all('tr')
        for row in rows:
            # Ищем заголовок строки (проверяем оба варианта класса)
            header = row.find('th', {'class': ['plainlist', None]})
            if not header:
                continue

            header_text = clean_text(header.get_text())
            if not header_text:
                continue

            print(f"\nОбработка строки с заголовком: {header_text}")

            # Ищем значение в строке (проверяем оба варианта класса)
            value_cell = row.find('td', {'class': ['plainlist', None]})
            if not value_cell:
                print("Ячейка со значением не найдена")
                continue

            print("Найдена ячейка со значением:")
            print(value_cell.prettify())

            # Обрабатываем дату рождения
            if 'Дата рождения' in header_text:
                date_span = value_cell.find('span', class_='nowrap')
                if date_span:
                    print("Найден span с датой рождения:")
                    print(date_span.prettify())
                    links = date_span.find_all('a')
                    date_parts = []
                    for link in links:
                        text = link.get_text().strip()
                        print(f"Найдена ссылка с текстом: {text}")
                        if text and not text.startswith('['):
                            date_parts.append(text)
                    if date_parts:
                        person_info['Дата рождения'] = ' '.join(date_parts)
                        print(f"Извлечена дата рождения: {person_info['Дата рождения']}")

            # Обрабатываем место рождения
            elif 'Место рождения' in header_text:
                # Сначала пробуем найти в ul
                place_ul = value_cell.find('ul')
                if place_ul:
                    print("Найден список с местом рождения:")
                    print(place_ul.prettify())
                    person_info['Место рождения'] = clean_text(place_ul.get_text())
                else:
                    print("Список не найден, извлекаем текст из ячейки")
                    # Если ul не найден, берем весь текст ячейки
                    person_info['Место рождения'] = clean_text(value_cell.get_text())
                print(f"Извлечено место рождения: {person_info['Место рождения']}")

            # Обрабатываем дату смерти
            elif 'Дата смерти' in header_text:
                date_span = value_cell.find('span', class_='nowrap')
                if date_span:
                    print("Найден span с датой смерти:")
                    print(date_span.prettify())
                    links = date_span.find_all('a')
                    date_parts = []
                    for link in links:
                        text = link.get_text().strip()
                        print(f"Найдена ссылка с текстом: {text}")
                        if text and not text.startswith('['):
                            date_parts.append(text)
                    if date_parts:
                        person_info['Дата смерти'] = ' '.join(date_parts)
                        print(f"Извлечена дата смерти: {person_info['Дата смерти']}")

            # Обрабатываем место смерти
            elif 'Место смерти' in header_text:
                # Сначала пробуем найти в ul
                place_ul = value_cell.find('ul')
                if place_ul:
                    print("Найден список с местом смерти:")
                    print(place_ul.prettify())
                    person_info['Место смерти'] = clean_text(place_ul.get_text())
                else:
                    print("Список не найден, извлекаем текст из ячейки")
                    # Если ul не найден, берем весь текст ячейки
                    person_info['Место смерти'] = clean_text(value_cell.get_text())
                print(f"Извлечено место смерти: {person_info['Место смерти']}")

        # Выводим итоговую информацию
        print("\nИтоговая информация:")
        for key, value in person_info.items():
            print(f"{key}: {value}")

        return person_info

    except Exception as e:
        print(f"Ошибка при обработке страницы: {e}")
        return None


def save_to_excel(data, filename='person_info.xlsx'):
    """Сохраняет данные в Excel файл"""
    try:
        df = pd.DataFrame([data])
        df.to_excel(filename, index=False)
        print(f'Данные сохранены в файл {filename}')
    except Exception as e:
        print(f"Ошибка при сохранении в Excel: {e}")


def main():
    try:
        urls = [
            'https://ru.wikipedia.org/wiki/Павлов,_Иван_Петрович',
            'https://ru.wikipedia.org/wiki/Аа,_Карл_Вильгельм_фон_дер',
            'https://ru.wikipedia.org/wiki/Абашин,_Сергей_Николаевич'
        ]

        for url in urls:
            print(f"\nОбработка страницы: {url}")
            person_info = get_person_info(url)

            if person_info:
                print("\nПолученная информация:")
                for key, value in person_info.items():
                    print(f"{key}: {value}")

                filename = f"person_info_{url.split('/')[-1]}.xlsx"
                save_to_excel(person_info, filename)
            else:
                print(f"Не удалось получить информацию для {url}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()