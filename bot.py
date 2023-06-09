from __future__ import annotations
from typing import Optional
import bale
from bale import Message, Update
from utils import persianNumbers, Components, ConfigParser, make_persian, messages, GroupBanUpdater
from cogs import Setting, Help, Filter, Commands, Support, Developer, ADS
from database import DB
from datetime import datetime

components = (
    Setting,
    Help,
    Filter,
    Commands,
    Support,
    Developer,
    ADS
)

with open("./config.json", "r", encoding="utf8") as _file:
    config = ConfigParser(_file.read())


class GroupBan(bale.Bot):
    def __init__(self):
        super().__init__(config.TOKEN, updater=GroupBanUpdater)
        self.config = config
        self.components = Components()
        self._start_time = datetime.now()
        self.command_usage_count = 0
        self.setup_events()
        self.make_persian = make_persian

    @property
    def developers(self):
        return config.DEVELOPER_IDS

    @property
    def base_messages(self):
        return messages

    @property
    def uptime(self):
        return datetime.now() - self._start_time

    def make_db(self):
        return DB(config.DATABASE)

    def setup_events(self):
        self.add_event(bale.EventType.READY, self.on_ready)
        self.add_event(bale.EventType.MESSAGE, self.when_developers_send_message)
        self.add_event(bale.EventType.UPDATE, self.on_update)

        for core in components:
            obj = core(self)
            result = obj.setup()
            for function in result:
                self.add_event("on_" + result[function], function)

    async def on_ready(self):
        print("Login as", self.user.username)

    async def on_update(self, update: bale.Update):
        print(update)

    async def when_developers_send_message(self, message: bale.Message):
        if not (message.author and message.content):
            return

        if int(message.author.chat_id) in self.developers:
            return self.dispatch("developer_message", message)

    async def get_updates(self, offset: int = None, limit: int = None) -> list["Update"]:
        return await super().get_updates(offset, limit)

    def get_ads(self, connection: "DB"):
        cursor = connection.cursor()
        cursor.execute("SELECT ads_id, description FROM ads WHERE visit_cnt != max_visit_cnt ORDER BY RAND() LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        if not result:
            return "❌ تبلیغی برای نمایش نیست"
        (ads_id, desc) = result
        self.dispatch("ads_enter", ads_id)
        return desc

    async def send_message(self, chat_id, text, *, components=None, reply_to_message_id: Optional[str | int] = None, convert: bool = True) -> "Message":
        """This service is used to send text messages.

        Parameters
        ----------
            chat_id: :class:`str` | :class:`int`
                Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            text: :class:`str`
                Text of the message to be sent. Max 4096 characters after entities parsing.
            components: Optional[:class:`bale.Components` | :class:`bale.RemoveComponents`]
                Message Components
            reply_to_message_id: Optional[:class:`str` | :class:`int`]
                Additional interface options. An object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
            convert: Optional[bool]
                a boolean param to set convetion status
        Returns
        -------
            :class:`bale.Message`
                The Message
        Raises
        ------
            NotFound
                Invalid Chat ID.
            Forbidden
                You do not have permission to send Message to this chat.
            APIError
                Send Message Failed.
        """
        if convert:
            for (persian_num, english_num) in persianNumbers:
                text = text.replace(english_num, persian_num)
        try:
            return await super().send_message(chat_id, text, components=components, reply_to_message_id=reply_to_message_id)
        except bale.BaleError as exc:
            if exc.message == "0: Internal server error":
                return await super().send_message(chat_id, text, components=components, reply_to_message_id=reply_to_message_id)

    async def send_message_without_convert(self, chat_id, text, components=None) -> "Message":
        return await self.send_message(chat_id, text, components=components, convert=False)

    async def edit_message(self, chat_id: str | int, message_id: str | int, text: str, *,
                           components = None) -> "Message":
        for (persian_num, english_num) in persianNumbers:
            text = text.replace(english_num, persian_num)
        try:
            return await super().edit_message(chat_id, message_id, text, components=components)
        except bale.BaleError as exc:
            if exc.message == "0: Internal server error":
                await self.delete_message(chat_id, message_id)
                return await self.send_message(chat_id, text)

if __name__ == "__main__":
    bot = GroupBan()
    bot.run(1)
