import aiosqlite


class CoreDB:
    def __init__(self, database_path):
        self.database_path = database_path

    async def get_database_connection(self):
        database_connection = await aiosqlite.connect(self.database_path)
        database_connection.row_factory = aiosqlite.Row
        return database_connection

    async def insert_pydantic_scheme(self, scheme, table_name):
        columns = ", ".join(scheme.dict().keys())  # As str "column1, column2, ... , columnN"
        values = list(scheme.dict().values())  # As list [value1, value2, ... , value]
        sql = f"INSERT INTO {table_name} " \
              f"({columns}) " \
              f"VALUES ({(len(values) * '?, ')[:-2]})"  # Forming a list of values (?, ?, ... ?) for secured SQL request
        db = await self.get_database_connection()
        await db.execute(sql, values)
        await db.commit()
        await db.close()

    async def select_fetchall(self, sql, data=None):
        db = await self.get_database_connection()
        cursor = await db.execute(sql, data)
        select = await cursor.fetchall()
        await db.close()
        return select

    async def select_fetchone(self, sql, data=None):
        db = await self.get_database_connection()
        cursor = await db.execute(sql, data)
        select = await cursor.fetchone()
        await db.close()
        return select

    async def delete(self, sql, data=None):
        db = await self.get_database_connection()
        await db.execute(sql, data)
        await db.commit()
        await db.close()
