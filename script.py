import requests
import time
import csv
import threading
from typing import List

# Установка интервала между запросами на создание отчета в 1 минуту
interval = 60

# Заголовок Authorization
headers = {'Authorization': 'Bearer 1d706f2b-d4cf-43cc-8a38-0ad4a8a97887'}

# URL для запросов
url = 'https://analytics.maximum-auto.ru/vacancy-test/api/v0.1'

# Список для хранения идентификаторов отчетов и времени их создания
reports = []

# Функция для отправки запроса на создание отчета
def create_report() -> None:
    while True:
        # Отправка запроса на создание отчета
        response = requests.post(url, headers=headers)

        # Обработка ответа со статусом 201
        if response.status_code == 201:
            # Добавление идентификатора отчета и времени его создания в список
            reports.append((response.json()['report_id'], time.time()))

        # Задержка перед следующим запросом
        time.sleep(interval)

# Функция для получения отчета и записи его в файл
def get_report(report_id: str, create_time: float) -> None:
    while True:
        # Отправка запроса на получение отчета
        response = requests.get(f"{url}/{report_id}", headers=headers)

        # Обработка ответа со статусом 200
        if response.status_code == 200:
            # Запись данных в файл
            with open('results.csv', 'a', newline='') as file:
                writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([create_time, response.json()['value']])
            break

        # Задержка перед следующим запросом
        time.sleep(1)

# Открытие файла для записи результатов
with open('results.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['date_time', 'value'])

    # Запуск потока для отправки запросов на создание отчетов
    t = threading.Thread(target=create_report)
    t.start()

    # Организация цикла для обработки готовых отчетов
    while True:
        for report in reports:
            # Получение и удаление записи из списка
            report_id, create_time = report
            reports.remove(report)

            # Запуск потока для получения отчета
            t = threading.Thread(target=get_report, args=(report_id, create_time))
            t.start()

        # Задержка перед следующей итерацией
        time.sleep(60) # Приостанавливаем выполнение на 60 секунд

        # Проверка наличия новых отчетов
        new_reports = get_report()

        # Добавление новых отчетов в список
        if new_reports:
            reports.extend(new_reports)