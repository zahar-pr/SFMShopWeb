import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(host=os.getenv("MONGO_HOST", "localhost"), port=int(os.getenv("MONGO_PORT", 27017)))
db = client["sfmshop_logs"]
logs_collection = db["logs"]


def save_log(log_data: dict):
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.now()
    return logs_collection.insert_one(log_data).inserted_id


def get_logs_by_status_code(status_code: int):
    return list(logs_collection.find({"status_code": status_code}))


def get_logs_by_date_range(start_date: datetime, end_date: datetime):
    return list(logs_collection.find({"timestamp": {"$gte": start_date, "$lte": end_date}}))


def get_logs_by_ip(ip: str):
    return list(logs_collection.find({"ip": ip}))


def get_logs_count_by_type():
    return list(logs_collection.aggregate([{"$group": {"_id": "$type", "count": {"$sum": 1}}}]))


def get_logs_count_by_status_code():
    return list(logs_collection.aggregate([{"$group": {"_id": "$status_code", "count": {"$sum": 1}}}]))


if __name__ == "__main__":
    save_log({"type": "ИНФО", "status_code": 200, "ip": "192.168.1.1", "message": "Товар получен"})
    save_log({"type": "ОШИБКА", "status_code": 500, "ip": "192.168.1.2", "message": "Внутренняя ошибка сервера"})
    save_log({"type": "ПРЕДУПРЕЖДЕНИЕ", "status_code": 404, "ip": "192.168.1.1", "message": "Не найдено"})

    print("Поиск по статусу 500:")
    print(get_logs_by_status_code(500))

    print("\nПоиск по IP:")
    print(get_logs_by_ip("192.168.1.1"))

    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    print("\nПоиск по диапазону дат:")
    print(get_logs_by_date_range(start_date, end_date))

    print("\nПодсчет по типам:")
    print(get_logs_count_by_type())

    print("\nПодсчет по статус-кодам:")
    print(get_logs_count_by_status_code())

    print("\nСтатистика по времени:")
    print(get_logs_time_statistics())
