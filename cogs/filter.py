import re
from typing import TYPE_CHECKING, Dict
import bale
from utils import UserRateLimit
if TYPE_CHECKING:
    from ..bot import GroupBan

class Filter:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot
        self.rate_limits: Dict[int, Dict[int, "UserRateLimit"]] = {}

    def setup(self):
        return {
            self.when_send_message_in_group: "message"
        }

    def chat_member_have_rate_limit(self, message: "bale.Message", chat_id: int, user_id: int) -> bool:
        ratelimit = self.rate_limits.get(chat_id, {}).get(user_id)
        if not ratelimit:
            if not self.rate_limits.get(chat_id):
                self.rate_limits[chat_id] = {}
            self.rate_limits[chat_id][user_id] = UserRateLimit()
            ratelimit = self.rate_limits[chat_id][user_id]

        return ratelimit.user_is_rate_limited(message)

    async def when_send_message_in_group(self, message: bale.Message):
        if not message.chat.type.is_group_chat():
            return self.bot.dispatch("verified_message", message)

        with self.bot.make_db() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT anti_spam, anti_link, anti_mention, anti_word, auto_answer FROM chat WHERE chat_id = '{}'".format(message.chat.chat_id))
            filters = cursor.fetchone()
            if not filters:
                return self.bot.dispatch("unverified_message", message)
            (anti_spam, anti_link, anti_mention, anti_word, auto_answer) = filters
            cursor.execute("SELECT word, answer FROM auto_answer WHERE chat_id = '{}'".format(message.chat.chat_id))
            auto_answer_dict = {word: answer for word, answer in cursor.fetchall()}
            cursor.execute("SELECT word FROM bad_words WHERE chat_id = '{}'".format(message.chat.chat_id))
            bad_words = [word for (word, ) in cursor.fetchall()]
        standard_content = self.bot.make_persian(message.content)
        try:
            member = await self.bot.get_chat_member(message.chat_id, message.author.user_id)
        except bale.BaleError:
            member = None
        if not member or not member.status.is_member():
            return self.bot.dispatch("verified_message", message)

        user_spam_state = self.chat_member_have_rate_limit(message, int(message.chat_id), int(message.author.user_id))
        if anti_spam and user_spam_state:
            return await message.delete()

        if (anti_link and re.search("(?P<url>https?://[^\s]+)", standard_content)) or (anti_mention and re.search("(?<=@)\w+", standard_content)):
            return await message.delete()

        if anti_word:
            for word in bad_words:
                if word in standard_content:
                    await message.delete()
                    break

        if auto_answer and auto_answer_dict.get(standard_content):
            return await message.chat.send(auto_answer_dict.get(standard_content))

        self.bot.dispatch("verified_message", message)
