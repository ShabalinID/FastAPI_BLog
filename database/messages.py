from models.models import MessageDB


class MessagesDatabase:
    def insert_pydantic_scheme(self, scheme, table_name):
        columns = ", ".join(scheme.dict().keys())  # As str "column1, column2, ... , columnN"
        values = list(scheme.dict().values())  # As list [value1, value2, ... , value]
        sql = f"INSERT INTO {table_name} " \
              f"({columns}) " \
              f"VALUES ({(len(values) * '?, ')[:-2]})"  # Forming a list of values (?, ?, ... ?) for secured SQL request
        self.cursor.execute(sql, values)
        self.connection.commit()

    async def get_all_messages(self):
        sql = "SELECT * " \
              "FROM messages " \
              "ORDER BY message_id DESC"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        messages = []
        for row in result:
            messages.append(MessageDB(**row))
        return messages

    async def get_message_details(self, message_id):
        sql = "SELECT * " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchone()
        return result

    async def insert_new_message(self, message: MessageDB):
        table_name = "messages"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=message)
