from typing import TYPE_CHECKING
import asyncio
import bale

if TYPE_CHECKING:
	from ..bot import GroupBan
	from ..database import DB


class Setup:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	def setup(self):
		return {
			self.when_message: "message"
		}

	async def when_message(self, message: bale.Message):
		if message.content == "/setup":
			if message.chat.type.is_private_chat():
				return await message.chat.send("🚀 * برای ستاپ کردن من داخل گروه خود، ابتدا من را به آن جا اضافه کرده و سپس برای ستاپ کردن ربات دستور /setup را وارد کنید *")

			return await self.when_send_setup(message)

	async def when_send_setup(self, message: bale.Message):
		check_message = await message.chat.send("📡 * در حال برقراری ارتباط با سرور... *\n😉 لطفا شکیبا باشید")
		try:
			admins = await message.chat.get_chat_administrators()
		except:
			return await check_message.edit("❌ *من فاقد دسترسی ادمین با دسترسی کامل هستم، لطفا دسترسی را داده و مجددا دستور را ارسال کنید!*")
		else:
			admins = [int(admin.user.chat_id) for admin in admins]
			if not int(message.author.user_id) in admins:
				return await check_message.edit("❌ *شما ادمین چت نیستید*")
			connection = self.bot.make_db()

			first_render = self.render_chat_info(connection, message.chat)
			if not first_render:
				return await check_message.edit("❌ *این چت در دیتابیس یافت نشد؛ لطفا ربات را کیک کرده و دوباره به گروه اضافه کنید*")

			await check_message.edit("🚀 *لطفا چت شخصی خود با ربات را بررسی نمائید*")

			try:
				render_message = await message.author.send(first_render)
				action_message = await message.author.send("🚀 * 🔷 *لطفا بخش مورد نظر خود را از طریق دکمه های زیر انتخاب کنید:*\n\n☝ شما میتوانید وضعیت فعلی امکانات ربات را به صورت زنده بررسی نمائید. *", components=self.bot.components.setup_command())
			except:
				return await check_message.edit("❌ *امکان ارسال پیام به شما وجود ندارد، لطفا محدودیت هارا برداشته و یا یک بار به ربات پیام بدهید*")

			while 1:
				try:
					action: bale.CallbackQuery = await self.bot.wait_for("callback", check = lambda c: c.user == message.author and c.message.message_id == action_message.message_id, timeout = 60.0)
				except asyncio.TimeoutError:
					await render_message.delete()
					await action_message.delete()
					break
				else:
					if action.data == "exit":
						await action_message.delete()
						break

					if not action.data in ["anti_spam", "anti_link", "anti_mention", "anti_word", "auto_answer"]:
						continue

					cursor = connection.cursor()
					cursor.execute("UPDATE chat SET {0} = !{0} WHERE chat_id = '{1}'".format(
						action.data,
						int(message.chat.chat_id)
					))
					connection.commit()

					await render_message.edit(self.render_chat_info(connection, message.chat))

			connection.close()
			return await render_message.reply("💠 *تعییرات با موفقیت اعمال شد*\nبرای ستاپ دوباره، میتوانید از دستور [/setup](send:/setup) استفاده کنید")


	def render_chat_info(self, connection: "DB", chat: bale.Chat):
		render_bool = lambda state: "فعال" if state else "غیر فعال"
		cursor = connection.cursor()
		cursor.execute("SELECT anti_spam, anti_link, anti_mention, anti_word, auto_answer FROM chat WHERE chat_id = '{}'".format(chat.chat_id))
		result = cursor.fetchone()
		if not result:
			return
		(anti_spam, anti_link, anti_mention, anti_word, auto_answer) = result

		return "💠 *ستاپ کردن ربات در گروه {}*\nشناسه یکتا گروه: {}\n\n👥 *اطلاعات گروه*\n🔧 آنتی اسپم: {}\n🔧 آنتی لینک: {}\n🔧 آنتی منشن: {}\n🔧 آنتی ورد: {}\n🔧 پاسخگویی خودکار: {}\n\n👇 *شما میتوانید با استفاده از دکمه های پیام زیر، تنظیمات را تغییر دهید.*".format(
			chat.title,
			chat.chat_id,
			render_bool(anti_spam),
			render_bool(anti_link),
			render_bool(anti_mention),
			render_bool(anti_word),
			render_bool(auto_answer)
		)
