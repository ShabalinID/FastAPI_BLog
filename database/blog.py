import os
import aiofiles
import mimetypes

from database.core import CoreDB
from models import Message, Media

MEDIA_PATH = "database/data/media/"


class MessagesDatabase(CoreDB):
    def get_all_messages(self):
        sql = "SELECT * " \
              "FROM messages " \
              "ORDER BY message_id DESC"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        messages = []
        for row in result:
            messages.append(Message(**row))
        return messages

    def get_message_details(self, message_id):
        sql = "SELECT * " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchone()
        return result

    def insert_new_message(self, message: Message):
        table_name = "messages"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=message)

    def is_author(self, message_id):
        sql = "SELECT author " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return

    def delete_message(self, message_id):
        sql = "DELETE FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        self.connection.commit()
        self.delete_message_media(message_id=message_id)

    def delete_message_media(self, message_id):
        media_list = self.get_media_list(message_id=message_id)
        for file in media_list:
            os.remove(os.getcwd() + "/" + MEDIA_PATH + file.media_url)
        sql = "DELETE FROM media " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        self.connection.commit()

    async def save_message_media(self, message, media_list):
        message_id = self.get_message_id(message=message)
        for num, file in enumerate(media_list):
            extension = self.get_media_extension(filename=file.filename)
            media_type = self.get_media_type(filename=file.filename)

            filename = f"{message.author}_{message.published}_{message_id}_{num}{extension}"
            await self.file_safe(file, filename)

            media = Media(media_url=filename,
                          media_type=media_type,
                          message_id=message_id)
            self.insert_media(media)

    def get_message_id(self, message):
        sql = "SELECT message_id " \
              "FROM messages " \
              "WHERE author=:message_author AND published=:message_published"
        self.cursor.execute(sql, {"message_author": message.author,
                                  "message_published": message.published})
        result = self.cursor.fetchone()[0]
        return result

    @staticmethod
    def get_media_extension(filename):
        extension = os.path.splitext(filename)[1]
        return extension

    @staticmethod
    def get_media_type(filename):
        media_type = mimetypes.guess_type(filename)[0]
        return media_type

    @staticmethod
    async def file_safe(file, filename):
        async with aiofiles.open(MEDIA_PATH + filename, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

    def insert_media(self, media: Media):
        table_name = "media"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=media)

    def get_media_list(self, message_id):
        sql = "SELECT * " \
              "FROM media " \
              "WHERE message_id=:message_id " \
              "ORDER BY media_id DESC"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchall()
        media_list = []
        for row in result:
            media_list.append(Media(**row))
        return media_list
