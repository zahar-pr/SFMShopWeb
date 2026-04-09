from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient


class LogService:
    def __init__(self, mongo_url="mongodb://localhost:27017", db_name="logs_db"):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        self.error_col = self.db["errors"]
        self.access_col = self.db["access"]

    async def log_error(self, message: str, stack_trace: str):
        await self.error_col.insert_one({
            "message": message,
            "stack_trace": stack_trace,
            "created_at": datetime.utcnow()
        })

    async def log_access(self, ip: str, endpoint: str, method: str):
        await self.access_col.insert_one({
            "ip": ip,
            "endpoint": endpoint,
            "method": method,
            "created_at": datetime.utcnow()
        })

    async def get_errors(self, start: datetime, end: datetime) -> list[dict]:
        cursor = self.error_col.find({"created_at": {"$gte": start, "$lte": end}})
        return await cursor.to_list(length=1000)

    async def get_access_logs(self, start: datetime, end: datetime) -> list[dict]:
        cursor = self.access_col.find({"created_at": {"$gte": start, "$lte": end}})
        return await cursor.to_list(length=1000)
