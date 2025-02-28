from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

DATABASE_URI = config('DATABASE_URI', cast=str, default=False)
DATABASE_NAME = "notifications_system"

class MongoDB:

    def __init__(self):
        self.client = None
        self.database = None

    async def connect(self):
        self.client = AsyncIOMotorClient(DATABASE_URI)
        self.database = self.client[DATABASE_NAME]

    async def close(self):
        if self.client:
            self.client.close()

    def get_database(self):
        return self.database
    

mongodb = MongoDB()

async def get_db():
    if mongodb.database is None:
        await mongodb.connect()
    return mongodb.get_database()
