from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
	from ..bot import GroupBan


class Help:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	@property
	def commands(self):
		return ["/start", "/help", "/donate"]

	@property
	def menu(self):
		return "\n".join(["⛏ * [دستورات](send:/commands) *",
		   "📔 * [داکیومنت ربات](https://groupban.ir/commands) *",
		   "💚 * [دونیت](send:/donate) *",
		   "✨ * [درباره گروه بان](send:/about) *"])

	@property
	def bot_news(self):
		return "\n".join(["*پشتیبانی گروه بان سعی در حل مشکلات ایجاد شده دارد*",
		   "امکاناتی از جمله شمارش اینوایت های کاربر در گروه، ولکامر ، داشبورد گروه در سایت و ... به زودی اضافه خواهند شد"])

	def ads(self, chat: bale.Chat):
		return "❌ تبلیغی برای نمایش وجود ندارد!"

	def setup(self):
		return {
			self.when_message: "verified_message",
			self.when_message_not_verified: "unverified_message",
			self.when_user_join_me: "member_chat_join",
			self.when_user_kicked_me: "member_chat_leave"
		}

	async def when_message(self, message: bale.Message):
		if message.content in ["/help", "/start"]:
			if message.chat.type.is_group_chat():
				return await message.reply("\n\n".join([
					"🤖 *گروه بان؛ مدرن ترین ربات مدیریت گروه*",
				   self.menu,
				   "\n".join(["📺 * تبلیغات - 💎 [رزرو تبلیغات](https://ble.ir/support_groupban) *", self.ads(message.chat)]),
				   "\n".join(["📰 *اخبار ربات*", self.bot_news]),
				   "⚖ *نقض قوانین «گروه بان» بن به همراه دارد.*"]), components=self.bot.components.site_and_support_buttons())
			return await message.author.send("🤖 *به ربات گروه بان خوش آمدید*\n\n💎 با اضافه کردن گروه بان به گروه، امنیت اعضای گروه را تضمین کنید!\n\n⚖ *نقض قوانین «گروه بان» بن به همراه دارد*", components=self.bot.components.help_command())

		elif message.content == "/donate":
			return await message.chat.send("❤ *دونیت به مجموعه گروه بان*\n\nشما میتوانید از طریق سرویس پرداخت امن آی دی پی (idpay) مبلغ مورد نظر خود را به مجموعه گروه بان اهدا نمائید.", components=bale.Components(inline_keyboards=[bale.InlineKeyboard("اهدا به مجموعه گروه بان", url="https://idpay.ir/group-ban")]))

		elif message.content == "/about":
			return await message.chat.send("〽 *درباره مجموعه گروه بان*\n\n👥 توسعه داده شده توسط *K.A - A.M - K.G*\n\n👨‍💻 این بازو به وسیله زبان قدرتمند *پایتون* و کتابخانه *python-bale-bot* طراحی و برنامه نویسی شده است. همچنین این پروژه به صورت متن باز (Open Source) در گیت هاب مجموعه قرار دارد.\n\n🔆 بهار 1402", components=self.bot.components.about_command())

	async def when_message_not_verified(self, message: bale.Message):
		if message.chat.type.is_group_chat():
			if message.content and message.content.startswith("/"):
				return await message.chat.send("❌ *متاستفم؛ امکان درک پیام شمارا ندارم*\n🚀 لطفا یک بار ربات را کیک کرده و مجددا به گروه دعوت نمائید. و در صورتی که مشکل برطرف نشد با پشتیبانی *گروه بان* ارتباط بگیرید.\n\n📞 [پشتیبانی](https://groupban.ir/support)")

		elif message.chat.type.is_private_chat():
			return await message.chat.send("❌ *متاستفم؛ امکان درک پیام شمارا ندارم*\n\n⭕ این یک مشکل جدی است و پیشنهاد میکنیم برای حل مشکل به پشتیبانی *گروه بان* مراجعه نمائید.\n\n📞 [پشتیبانی](https://groupban.ir/support)")

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
			except bale.BaleError:
				return await inviter.send("سلام، من ربات گروه بان هستم.\nشما من را عضو گروه کبابی محمد و پسران کرده اید.\n\n❌ *برای شروع کار با ربات و تشخیص ادمینان گروه، من را ادمین (همه دسترسی ها) نمائید.*\n\n[سایت ربات گروه بان](https://groupban.ir)")

	async def when_user_kicked_me(self, message: bale.Message, chat: bale.Chat, user: bale.User):
		if chat.type.is_group_chat() and user.user_id == self.bot.user.user_id:
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("DELETE FROM chat WHERE chat_id = '{}'".format(chat.chat_id))
				connection.commit()
				cursor.close()
