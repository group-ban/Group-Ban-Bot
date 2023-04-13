from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
	from ..bot import GroupBan


class Help:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	def setup(self):
		return {
			self.when_message: "message",
			self.when_user_join_me: "member_chat_join",
			self.when_user_kicked_me: "member_chat_leave"
		}

	async def when_message(self, message: bale.Message):
		if message.content == "/help":
			if message.chat.type.is_group_chat():
				return await message.reply("🚀 * لطفا دستور مورد نظر را در پی وی ربات بدهید *")
			return await message.author.send('🤖 *به ربات گروه بان خوش آمدید*\n👇 لطفا از طریق دکمه های زیر، کارکرد خود را *انتخاب* نمائید، و یا در صورتی که با ربات آشنایی ندارید بر روی گزینه *"راهنما"* کلیک نمائید.', components=self.bot.components.help_command())

	async def when_user_join_me(self, message: bale.Message, chat: bale.Chat, user: bale.User):
		if chat.type.is_group_chat() and user.user_id == self.bot.user.user_id:
			inviter: bale.User = message.from_user
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("INSERT INTO chat(chat_id) VALUES (%s)", (int(chat.chat_id), ))
				connection.commit()
				cursor.close()

			try:
				await chat.send("سلام؛ من ربات گروه بان هستم.\nاحتمالا تعریف من رو زیاد شنیدی 😎\n\n❌ *برای شروع کار با ربات و تشخیص ادمینان گروه، من را ادمین (همه دسترسی ها) نمائید.*\n\n💻 [سایت ربات گروه بان](https://groupban.ir)")
			except:
				return await inviter.send("سلام، من ربات گروه بان هستم.\nشما من را عضو گروه کبابی محمد و پسران کرده اید.\n\n❌ *برای شروع کار با ربات و تشخیص ادمینان گروه، من را ادمین (همه دسترسی ها) نمائید.*\n\n[سایت ربات گروه بان](https://groupban.ir)")

	async def when_user_kicked_me(self, message: bale.Message, chat: bale.Chat, user: bale.User):
		if chat.type.is_group_chat() and user.user_id == self.bot.user.user_id:
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("DELETE FROM chat WHERE chat_id = '{}'".format(chat.chat_id))
				connection.commit()
				cursor.close()
