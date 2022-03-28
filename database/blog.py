import os
import aiofiles
import mimetypes

from database.core import CoreDB
from models import Message, Media, Like

MEDIA_PATH = "database/data/media/"


class BlogDatabase(CoreDB):

    #  Message operations
    async def insert_new_message(self, message: Message):
        table_name = "messages"
        await self.insert_pydantic_scheme(table_name=table_name, scheme=message)

    async def get_all_messages(self):
        sql = "SELECT * " \
              "FROM messages " \
              "ORDER BY message_id DESC"
        select = await self.select_fetchall(sql=sql)
        messages = []
        for row in select:
            messages.append(Message(**row))
        return messages

    async def get_message_details(self, message_id):
        sql = "SELECT * " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        data = {"message_id": message_id}
        select = await self.select_fetchone(sql=sql, data=data)
        return select

    async def is_author(self, message_id):
        sql = "SELECT author " \
              "FROM messages " \
              "WHERE message_id=:message_id"
        data = {"message_id": message_id}
        select = await self.select_fetchone(sql=sql, data=data)
        return select

    async def get_message_id(self, message):
        sql = "SELECT message_id " \
              "FROM messages " \
              "WHERE author=:message_author AND published=:message_published"
        data = {"message_author": message.author,
                "message_published": message.published}
        select = await self.select_fetchone(sql=sql, data=data)
        return select[0]

    async def delete_message(self, message_id):
        sql = "DELETE FROM messages " \
              "WHERE message_id=:message_id"

        data = {"message_id": message_id}
        await self.delete(sql=sql, data=data)

    #  Media operations
    async def save_message_media(self, message, media_list):
        message_id = await self.get_message_id(message=message)
        for num, file in enumerate(media_list):
            #  save media file
            extension = self.get_media_extension(filename=file.filename)
            media_type = self.get_media_type(filename=file.filename)
            file_path = os.getcwd() + "/" + MEDIA_PATH
            filename = f"{message.author}_" \
                       f"{message.published}_" \
                       f"{message_id}_" \
                       f"{num}" \
                       f"{extension}"  # e.g. admin_26-03-2022_00:07:26_105_0.jpeg
            await self.file_save(file, filename)
            #  insert data about media to the db
            media = Media(media_url=file_path + filename,
                          media_type=media_type,
                          message_id=int(message_id))
            await self.insert_media(media)

    @staticmethod
    def get_media_extension(filename):
        extension = os.path.splitext(filename)[1]
        return extension

    @staticmethod
    def get_media_type(filename):
        media_type = mimetypes.guess_type(filename)[0]
        return media_type

    @staticmethod
    async def file_save(file, filename):
        async with aiofiles.open(MEDIA_PATH + filename, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

    async def insert_media(self, media: Media):
        table_name = "media"
        await self.insert_pydantic_scheme(table_name=table_name, scheme=media)

    async def get_media_list(self, message_id):
        sql = "SELECT * " \
              "FROM media " \
              "WHERE message_id=:message_id " \
              "ORDER BY media_id DESC"
        data = {"message_id": message_id}
        select = await self.select_fetchall(sql=sql, data=data)
        media_list = []
        for row in select:
            media_list.append(Media(**row))
        return media_list

    async def delete_message_media(self, message_id):
        media_list = await self.get_media_list(message_id=message_id)
        for file in media_list:
            os.remove(file.media_url)
        sql = "DELETE FROM media " \
              "WHERE message_id=:message_id"
        data = {"message_id": message_id}
        await self.delete(sql=sql, data=data)

    #  Like operations
    async def get_message_likes(self, message_id):
        sql = "SELECT COUNT(message_id) as Likes " \
              "FROM likes " \
              "WHERE message_id=:message_id"
        data = {"message_id": message_id}
        select = await self.select_fetchone(sql=sql, data=data)
        return select[0]

    async def message_is_liked(self, message_id, username):
        sql = "SELECT * " \
              "FROM likes " \
              "WHERE message_id=:message_id AND username=:username"
        data = {"message_id": message_id, "username": username}
        select = await self.select_fetchone(sql=sql, data=data)
        return select

    async def insert_like(self, message_id, username):
        table_name = "likes"
        like = Like(message_id=message_id,
                    username=username)
        await self.insert_pydantic_scheme(table_name=table_name, scheme=like)

    async def unlike_message(self, message_id, username):
        sql = "DELETE FROM likes " \
              "WHERE message_id=:message_id AND username=:username"
        data = {"message_id": message_id, "username": username}
        await self.delete(sql=sql, data=data)
