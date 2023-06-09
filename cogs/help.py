from typing import TYPE_CHECKING
import bale
from datetime import timedelta

if TYPE_CHECKING:
	from ..bot import GroupBan

def parse_time(_datetime: "timedelta"):
	minutes = _datetime.seconds // 60
	return ("تقریبا {} ساعت".format(_datetime.seconds // 3600) if _datetime.seconds // 3600 > 0 else "{} دقیقه".format(minutes)) if minutes != 0 else "{} ثانیه".format(_datetime.seconds)

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
		return "\n".join(["*گروه بان به زودی اشتراکی میشود*\nاطلاعات بیشتر در [کانال اطلاع رسانی](https://ble.ir/groupban/5063234390369018/1684157208186)"])


	def setup(self):
		return {
			self.when_message: "verified_message",
			self.when_message_not_verified: "unverified_message",
			self.when_user_join_me: "member_chat_join",
			self.when_user_kicked_me: "member_chat_leave"
		}

	async def when_message(self, message: bale.Message):
		if not message.content:
			return

		if message.content and message.content.startswith("/"):
			self.bot.command_usage_count += 1

		if message.content.lower() in ["/help", "/start", self.bot.user.mention.lower()]:
			if message.chat.type.is_group_chat():
				with self.bot.make_db() as connection:
					return await self.bot.send_message_without_convert(message.chat_id, "\n\n".join([
						"*⚜ شروع | [منوی دستورات](send:/commands) | [درباره گروه بان](send:/about)*",
					   self.menu,
					   "\n".join(["📺 * تبلیغات - 💎 [رزرو تبلیغات](https://ble.ir/support_groupban2) *", self.bot.get_ads(connection)]),
					   "\n".join(["📰 *اخبار ربات*", self.bot_news]),
					   "⚖ *نقض قوانین «گروه بان» بن به همراه دارد.*\n🛡 با گروه بان امنیت اعضای گروهتو تضمین کن!"]), components=self.bot.components.site_and_support_buttons())
			return await self.bot.send_message_without_convert(message.chat_id, "🤖 *به ربات گروه بان خوش آمدید*\n\n💎 با اضافه کردن گروه بان به گروه، امنیت اعضای گروه را تضمین کنید!\n\n⚖ *نقض قوانین «گروه بان» بن به همراه دارد*", self.bot.components.help_command())

		elif message.content == "/donate":
			return await message.chat.send("❤ *دونیت به مجموعه گروه بان*\n\nشما میتوانید از طریق سرویس پرداخت امن آی دی پی (idpay) مبلغ مورد نظر خود را به مجموعه گروه بان اهدا نمائید.", components=bale.Components(inline_keyboards=[bale.InlineKeyboard("اهدا به مجموعه گروه بان", url="https://idpay.ir/group-ban")]))

		elif message.content == "/ping":
			return await message.chat.send("🏓 *پونگ*\n\n*آپتایم* : {}\n*دستورات استفاده شده* : {}\n\n✨ گروه بان؛ مدرن ترین ربات مدیریت گروه در بله".format(parse_time(self.bot.uptime), self.bot.command_usage_count))

		elif message.content == "/about":
			return await message.chat.send("*⚜ [شروع](send:/help) | [منوی دستورات](send:/commands) | درباره گروه بان*\n\n〽 *درباره مجموعه گروه بان*\n\n👥 توسعه داده شده توسط *کیان احمدیان و امین شهرابی*\n🎨 گرافیک، استاتیک و لوگو: *کسری گماسایی*\n\n👨‍💻 این بازو به وسیله زبان قدرتمند *پایتون* و کتابخانه *python-bale-bot* طراحی و برنامه نویسی شده است. همچنین این پروژه به صورت متن باز (Open Source) در گیت هاب مجموعه قرار دارد.\n\n🔆 بهار ۱۴۰۲", components=self.bot.components.about_command())

	async def when_message_not_verified(self, message: bale.Message):
		if message.chat.type.is_group_chat():
			if message.content and message.content.startswith("/"):
				return await message.chat.send("❌ *متاستفم؛ امکان درک پیام شمارا ندارم*\n🚀 لطفا یک بار ربات را کیک کرده و مجددا به گروه دعوت نمائید. و در صورتی که مشکل برطرف نشد با پشتیبانی *گروه بان* ارتباط بگیرید.\n\n📞 [پشتیبانی](https://groupban.ir/support)")

		elif message.chat.type.is_private_chat():
			return await message.chat.send("❌ *متاستفم؛ امکان درک پیام شمارا ندارم*\n\n⭕ این یک مشکل جدی است و پیشنهاد میکنیم برای حل مشکل به پشتیبانی *گروه بان* مراجعه نمائید.\n\n📞 [پشتیبانی](https://groupban.ir/support)")

	async def when_user_join_me(self, message: bale.Message, chat: bale.Chat, user: bale.User):
		if chat.type.is_group_chat() and user.user_id == self.bot.user.user_id:
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("SELECT * FROM chat WHERE chat_id = '{}'".format(int(chat.chat_id)))
				if not cursor.fetchone():
					cursor.execute("INSERT INTO chat(chat_id) VALUES (%s)", (int(chat.chat_id), ))
					connection.commit()
				cursor.close()

			await chat.send("✋ سلام، من گروه بان هستم.\n✨ ابتدا، لازمه داخل گروه من رو 👮‍♂️ *ادمین* (تمامی مجوز ها) کنید.\n\n👁 سپس از طریق نسخه موبایل، در بخش *اعضای گروه* با انتخاب *گروه بان* و کلیک بر روی *تغییر دسترسی بازو* ، سطح دریافتی پیام هارا بر روی *همه* بگذارید.\n\n💯 حالا کافیه دستور [/help](send:/help) رو بزنی و از امکانات من لذت ببری!\n\n```[دلیل داشتن تمامی دسترسی ها در ربات گروه بات چیست؟]لزوم داشتن هر یک از دسترسی های بخش *مدیران* به این شرح زیر می باشد:\n\n🔧 دلیل داشتن مجوز *دریافت اطلاعات کانال، ارسال و سنجاق پیام* ، کاملا عادی و مشخص است. این ربات به دلیل اقدامات مدیریتی خود، می بایست در هر لحظه آماده جلوگیری از تخریب گروه باشد. و به همین دلیل لزوم داشتن مجوز های *حذف پیام های گروه* و *حذف اعضا* در این امر کاملا واضح است. در بعضی مواقع و در اینوایت شماری و یا خدمات *دعوت فوری* نیز، نیاز است تا ربات مجوز *افزودن اعضا* را به همین جهت داشته باشد.\n\n🛡 امید است با تهیه و توسعه این بازو، کمکی کوچک به ادمینان و گروه داران عزیزمان بنمائیم.```", components=self.bot.components.site_and_support_buttons())

	async def when_user_kicked_me(self, message: bale.Message, chat: bale.Chat, user: bale.User):
		if chat.type.is_group_chat() and user.user_id == self.bot.user.user_id:
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("DELETE FROM chat WHERE chat_id = '{}'".format(chat.chat_id))
				connection.commit()
				cursor.close()
