import os
import aiofiles
import mimetypes

from database.core import CoreDB
from models import Message, Media, Like

MEDIA_PATH = "database/data/media/"


class BlogDatabase(CoreDB):

    #  Message operations
    def insert_new_message(self, message: Message):
        table_name = "messages"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=message)

    async def get_all_messages(self):
        sql = "SELECT * " \
              "FROM messages " \
              "ORDER BY message_id DESC"
        db = await self.get_database_connection()
        cursor = await db.execute(sql)
        result = await cursor.fetchall()
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

    def is_author(self, message_id):
        sql = "SELECT author " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchone()[0]
        return result

    def delete_message(self, message_id):
        sql = "DELETE FROM messages " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        self.cursor.commit()
        self.delete_message_media(message_id=message_id)

    #  Media operations
    async def save_message_media(self, message, media_list):
        message_id = self.get_message_id(message=message)
        for num, file in enumerate(media_list):
            extension = self.get_media_extension(filename=file.filename)
            media_type = self.get_media_type(filename=file.filename)

            file_path = os.getcwd() + "/" + MEDIA_PATH
            filename = f"{message.author}_" \
                       f"{message.published}_" \
                       f"{message_id}_" \
                       f"{num}" \
                       f"{extension}"  # e.g. admin_26-03-2022_00:07:26_105_0.jpeg
            await self.file_safe(file, filename)

            media = Media(media_url=file_path + filename,
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

    def delete_message_media(self, message_id):
        media_list = self.get_media_list(message_id=message_id)
        for file in media_list:
            os.remove(file.media_url)
        sql = "DELETE FROM media " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        self.cursor.commit()

    #  Like operations
    def get_message_likes(self, message_id):
        sql = "SELECT COUNT(message_id) as Likes " \
              "FROM likes " \
              "WHERE message_id=:message_id"
        self.cursor.execute(sql, {"message_id": message_id})
        result = self.cursor.fetchone()[0]
        return result
        pass

    def message_is_liked(self, message_id, username):
        sql = "SELECT * " \
              "FROM likes " \
              "WHERE message_id=:message_id AND username=:username"
        self.cursor.execute(sql, {"message_id": message_id, "username": username})
        result = self.cursor.fetchone()
        return result

    def insert_like(self, message_id, username):
        table_name = "likes"
        like = Like(message_id=message_id,
                    username=username)
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=like)

    async def unlike_message(self, message_id, username):
        sql = "DELETE FROM likes " \
              "WHERE message_id=:message_id AND username=:username"
        data = {"message_id": message_id, "username": username}
        await self.delete(sql=sql, data=data)
