from models import User
from database.core import CoreDB


class UserDatabase(CoreDB):
    async def insert_new_user(self, user: User):
        table_name = "users"
        await self.insert_pydantic_scheme(table_name=table_name, scheme=user)

    async def get_user_name_id(self, username):
        sql = "SELECT user_id " \
              "FROM users " \
              "WHERE username=:username"
        data = {"username": username}
        select = await self.select_fetchone(sql=sql, data=data)
        return select[0]

    async def username_is_taken(self, username):
        sql = "SELECT username " \
              "FROM users " \
              "WHERE username=:username"
        data = {"username": username}
        select = await self.select_fetchone(sql=sql, data=data)
        return select

    async def get_user(self, username):
        sql = "SELECT * " \
              "FROM users " \
              "WHERE username=:username"
        data = {"username": username}
        select = await self.select_fetchone(sql=sql, data=data)
        return select
