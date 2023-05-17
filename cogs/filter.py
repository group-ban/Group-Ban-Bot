import re
from typing import TYPE_CHECKING, Dict, Callable
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
            self.when_send_message_in_group: "message",
            self.when_message_edited_in_group: "edited_message"
        }

    def chat_member_have_rate_limit(self, message: "bale.Message", chat_id: int, user_id: int) -> bool:
        ratelimit = self.rate_limits.get(chat_id, {}).get(user_id)
        if not ratelimit:
            if not self.rate_limits.get(chat_id):
                self.rate_limits[chat_id] = {}
            self.rate_limits[chat_id][user_id] = UserRateLimit()
            ratelimit = self.rate_limits[chat_id][user_id]

        return ratelimit.user_is_rate_limited(message)

    async def do_after_check_chat_member(self, core: "Callable", message: "bale.Message", *args):
        try:
            member = await self.bot.get_chat_member(message.chat_id, message.author.user_id)
        except bale.BaleError:
            member = None
        else:
            if not member.status.is_member():
                member = None

        if member:
            return await core(*args)
        return self.bot.dispatch("verified_message", message)

    async def when_send_message_in_group(self, message: bale.Message):
        if not message.author or message.message_id == 0:
            return
        if not message.chat.type.is_group_chat():
            return self.bot.dispatch("verified_message", message)

        with self.bot.make_db() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT anti_spam, anti_link, anti_mention, anti_word, anti_forward, anti_code, auto_answer FROM chat WHERE chat_id = '{}'".format(message.chat.chat_id))
            filters = cursor.fetchone()
            if not filters:
                return self.bot.dispatch("unverified_message", message)
            standard_content = self.bot.make_persian(message.content)
            (anti_spam, anti_link, anti_mention, anti_word, anti_forward, anti_code, auto_answer) = filters
            cursor.execute("SELECT answer FROM auto_answer WHERE chat_id = '{}' AND word = '{}'".format(message.chat.chat_id, standard_content))
            auto_answer_result = cursor.fetchone()
            cursor.execute("SELECT word FROM bad_words WHERE chat_id = '{}'".format(message.chat.chat_id))
            bad_words = [word for (word,) in cursor.fetchall()]

        user_spam_state = self.chat_member_have_rate_limit(message, int(message.chat_id), int(message.author.user_id))

        if ( (anti_spam and user_spam_state) or
            (anti_link and (re.search("(?P<url>https?://\S+)", standard_content, flags=re.IGNORECASE) or re.search("(?P<url>ble.ir)", standard_content, flags=re.IGNORECASE)) ) or
            (anti_mention and re.search("(?<=@)\w+", standard_content)) or
            (anti_forward and (message.forward_from_message_id or message.forward_from or message.forward_from_chat)) or
            (anti_code and len(standard_content) > 500) ):
            return await self.do_after_check_chat_member(message.delete, message)

        if anti_word:
            for word in bad_words:
                if word in standard_content:
                    await self.do_after_check_chat_member(message.delete, message)
                    break

        if auto_answer and auto_answer_result:
            return await self.do_after_check_chat_member(self.bot.send_message_without_convert, message, message.chat_id, (message.author.mention or message.author.first_name) + "\n" + auto_answer_result[0])

        self.bot.dispatch("verified_message", message)

    async def when_message_edited_in_group(self, message: bale.Message):
        if not (message.content and message.author and message.author != self.bot.user):
            return

        with self.bot.make_db() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT anti_link, anti_mention, anti_word, anti_code FROM chat WHERE chat_id = '{}'".format(message.chat.chat_id))
            filters = cursor.fetchone()
            if not filters:
                return
            standard_content = self.bot.make_persian(message.content)
            (anti_link, anti_mention, anti_word, anti_code) = filters
            cursor.execute("SELECT word FROM bad_words WHERE chat_id = '{}'".format(message.chat.chat_id))
            bad_words = [word for (word,) in cursor.fetchall()]

        if ( (anti_link and (re.search("(?P<url>https?://\S+)", standard_content, flags=re.IGNORECASE) or re.search("(?P<url>ble.ir)", standard_content, flags=re.IGNORECASE)) ) or
            (anti_mention and re.search("(?<=@)\w+", standard_content)) or
            (anti_code and len(standard_content) > 500) ):
            return await self.do_after_check_chat_member(message.delete, message)

        if anti_word:
            for word in bad_words:
                if word in standard_content:
                    await self.do_after_check_chat_member(message.delete, message)
                    break