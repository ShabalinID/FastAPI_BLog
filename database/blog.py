from models import Message
from database.core import CoreDB


class MessagesDatabase(CoreDB):
    async def get_all_messages(self):
        sql = "SELECT * " \
              "FROM messages " \
              "ORDER BY message_id DESC"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        messages = []
        for row in result:
            messages.append(Message(**row))
        return messages

    async def get_message_details(self, message_id):
        sql = "SELECT * " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchone()
        return result

    async def insert_new_message(self, message: Message):
        table_name = "messages"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=message)
