import re
from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
    from ..bot import GroupBan

class Admin:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot
        self.convert_manager = bot.convert_manager

    def setup(self):
        return {
            self.when_send_message_in_group: "message"
        }

    async def when_send_message_in_group(self, message: bale.Message):
        if not message.chat.type.is_group_chat():
            return
        

        with self.bot.make_db() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT anti_link, anti_mention, anti_word, auto_answer FROM chat WHERE chat_id = '{}'".format(message.chat.chat_id))
            filters = cursor.fetchone()
            if not filters:
                return
            cursor.execute("SELECT word, answer FROM auto_answer WHERE chat_id = '{}'".format(message.chat.chat_id))
            auto_answer_dict = {word: answer for word, answer in cursor.fetchall()}
            (anti_link, anti_mention, anti_word, auto_answer) = filters

            cursor.execute("SELECT word, answer FROM bad_words WHERE chat_id = '{}'".format(message.chat.chat_id))
            bad_words = {word: word for word in cursor.fetchall()}
            for word in bad_words:
                if word == self.convert_manager.make_persian( message.content):
                    return await message.delete()

        member = await self.bot.get_chat_member(message.chat_id, message.author.user_id)
        if not member or not member.status.is_member():
            return

        if (anti_link and re.search("(?P<url>https?://[^\s]+)", message.content)) or (anti_mention and re.search("(?<=@)\w+", message.content)):
            return await message.delete()

        if auto_answer and auto_answer_dict.get(message.content):
            return await message.chat.send(message.content)