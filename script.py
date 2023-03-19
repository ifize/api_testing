import requests
import time
import csv
from datetime import datetime

TOKEN = "1d706f2b-d4cf-43cc-8a38-0ad4a8a97887"
API_URL = "https://analytics.maximum-auto.ru/vacancy-test/api/v0.1"

def create_report(report_id):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {"id": report_id}
    response = requests.post(f"{API_URL}/reports", headers=headers, json=data)
    if response.status_code == 201:
        return True
    elif response.status_code == 409:
        return False
    else:
        raise Exception("Failed to create report")

def get_report(report_id):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{API_URL}/reports/{report_id}", headers=headers)
    if response.status_code == 200:
        return response.json()["value"]
    elif response.status_code == 202:
        return None
    else:
        raise Exception("Failed to get report")

def delete_report(report_id):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.delete(f"{API_URL}/reports/{report_id}", headers=headers)
    if response.status_code != 204:
        raise Exception("Failed to delete report")

def write_to_csv(date_time, value):
    with open("results.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date_time, value])

while True:
    # Создаем новый отчет
    report_id = str(time.time())
    while not create_report(report_id):
        report_id = str(time.time())

    # Запоминаем время создания отчета
    report_time = time.time()

    # Опрашиваем API до получения готового отчета
    while True:
        # Получаем текущее значение отчета
        report_value = get_report(report_id)
        if report_value is None:
            time.sleep(1)
            continue

        # Если отчет готов, записываем его в CSV-файл и удаляем его
        write_to_csv(report_time, report_value)
        delete_report(report_id)
        break

    # Ждем 1 минуту перед созданием нового отчета
    time.sleep(60)
