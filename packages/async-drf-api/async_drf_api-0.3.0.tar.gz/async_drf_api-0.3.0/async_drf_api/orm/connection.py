
import asyncio

from async_drf_api.conf import get_settings

class Database:
    _instance = None
    _connection = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self, db_path=':memory:'):
        # 优先使用外部 settings 中的数据库名
        if db_path == ':memory:':
            settings = get_settings()
            db_path = settings.DATABASE_NAME
        if self._connection is None:
            import aiosqlite
            self._connection = await aiosqlite.connect(db_path)
            self._connection.row_factory = aiosqlite.Row
        return self._connection
    
    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def execute(self, query, params=None):
        # Ensure the database connection is initialized before executing any queries
        if self._connection is None:
            await self.connect()
        async with self._lock:
            cursor = await self._connection.execute(query, params or [])
            await self._connection.commit()
            return cursor
    
    async def fetch(self, query, params=None):
        cursor = await self.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def fetchone(self, query, params=None):
        cursor = await self.execute(query, params)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def get_connection(self):
        if self._connection is None:
            await self.connect()
        return self._connection

