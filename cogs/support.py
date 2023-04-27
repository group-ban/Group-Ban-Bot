from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
    from ..bot import GroupBan


class Support:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    @property
    def commands(self):
        return ["/helpme", ]

    def setup(self):
        return {
            self.when_send_command: "verified_message"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content in self.commands:
            return

        if not message.chat.type.is_group_chat():
            return await message.chat.send(self.bot.base_messages["only_group"])

        if message.content == "/helpme":
            return await message.chat.send("💼 *ربات در حال بروزرسانی سیستمی است. این کار تنها در هنگام قرار گیری ربات بر روی نسخه استیبل امکان پذیر است*")
