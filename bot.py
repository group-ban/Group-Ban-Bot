from __future__ import annotations
from typing import Optional
import bale
from bale import Message
from cogs import Admin, Help
from utils import persianNumbers, Components, ConfigParser
from database import DB

components = (
    Admin,
    Help
)

with open("./config.json", "r", encoding="utf8") as _file:
    config = ConfigParser(_file.read())


class GroupBan(bale.Bot):
    def __init__(self):
        super().__init__(config.TOKEN)
        self.config = config
        self.components = Components()
        self.setup_events()

    def make_db(self):
        return DB(config.DATABASE)

    def setup_events(self):
        self.add_event(bale.EventType.READY, self.on_ready)

        for core in components:
            obj = core(self)
            result = obj.setup()
            for function in result:
                self.add_event("on_" + result[function], function)

    async def on_ready(self):
        print("Login as", self.user.username)

    async def send_message(self, chat_id, text, *, components=None, reply_to_message_id: Optional[str | int] = None) -> "Message":
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
        for (persian_num, english_num) in persianNumbers:
            text = text.replace(english_num, persian_num)
        return await super().send_message(chat_id, text, components=components,
                                          reply_to_message_id=reply_to_message_id)


bot = GroupBan()
bot.run()
