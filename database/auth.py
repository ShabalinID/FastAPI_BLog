from models.models import User


class AuthDatabase:
    def insert_pydantic_scheme(self, scheme, table_name):
        columns = ", ".join(scheme.dict().keys())  # As str "column1, column2, ... , columnN"
        values = list(scheme.dict().values())  # As list [value1, value2, ... , value]
        sql = f"INSERT INTO {table_name} " \
              f"({columns}) " \
              f"VALUES ({(len(values) * '?, ')[:-2]})"  # Forming a list of values (?, ?, ... ?) for secured SQL request
        self.cursor.execute(sql, values)
        self.connection.commit()

    async def get_user_name_id(self, username):
        sql = "SELECT user_id " \
              "FROM users " \
              "WHERE username=:username"
        self.cursor.execute(sql, {"username": username})
        result = self.cursor.fetchone()[0]
        return result

    async def username_is_taken(self, username):
        sql = "SELECT username " \
              "FROM users " \
              "WHERE username=:username"
        self.cursor.execute(sql, {"username": username})
        result = self.cursor.fetchone()
        return result

    async def insert_new_user(self, user: User):
        table_name = "users"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=user)

    async def get_user_password(self, username):
        sql = "SELECT hashed_password " \
              "FROM users " \
              "WHERE username=:username"
        self.cursor.execute(sql, {"username": username})
        result = self.cursor.fetchone()[0]
        return result
