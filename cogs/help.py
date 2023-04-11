from typing import TYPE_CHECKING
import bale
from bale.error import Forbidden

if TYPE_CHECKING:
	from ..bot import GroupBan


class Help:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	def setup(self):
		return {
			self.when_message: "message"
		}

	async def when_message(self, message: bale.Message):
		if message.content == "/help":
			if message.chat.type.is_group_chat():
				return await message.reply("🚀 * پاسخ دستور فوق در پی وی، داده شد *")

			return await message.author.send('🤖 *به ربات گروه بان خوش آمدید*\n👇 لطفا از طریق دکمه های زیر، کارکرد خود را *انتخاب* نمائید، و یا در صورتی که با ربات آشنایی ندارید بر روی گزینه *"راهنما"* کلیک نمائید.', components=self.bot.components.help_command())
