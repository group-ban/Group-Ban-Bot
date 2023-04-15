from typing import TYPE_CHECKING
import bale
import asyncio
if TYPE_CHECKING:
	from ..bot import GroupBan, DB


def render_chat_info(connection: "DB", chat: bale.Chat):
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


class Admin:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	@property
	def commands(self):
		return {"/setup": self.group_setup, "/aa-add": self.auto_answer_add, "/aa-remove": self.auto_answer_remove}

	def setup(self):
		return {
			self.when_admin_send_message: "message"
		}

	async def when_admin_send_message(self, message: bale.Message):
		if not message.content in self.commands:
			return

		if not message.chat.type.is_group_chat():
			return await message.chat.send("❌ *این دستور تنها مختص به گروه های دارای ربات گروهبان میباشد*")

		check_message = await message.chat.send(self.bot.base_messages["wait"])
		try:
			member = await message.chat.get_chat_member(message.author)
		except:
			return await check_message.edit(
				"❌ *من فاقد دسترسی ادمین با دسترسی کامل هستم، لطفا دسترسی را داده و مجددا دستور را ارسال کنید!*")
		else:
			if member.status.is_member():
				return await check_message.edit("❌ *شما ادمین چت نیستید*")


	async def group_setup(self, message: bale.Message, check_message: bale.Message):
		connection = self.bot.make_db()

		first_render = render_chat_info(connection, message.chat)
		if not first_render:
			return await check_message.edit("❌ *این چت در دیتابیس یافت نشد؛ لطفا ربات را کیک کرده و دوباره به گروه اضافه کنید*")

		try:
			render_message = await message.author.send(first_render)
			action_message = await message.author.send("🚀 🔷 *لطفا بخش مورد نظر خود را از طریق دکمه های زیر انتخاب کنید:*\n\n☝ شما میتوانید وضعیت فعلی امکانات ربات را به صورت زنده بررسی نمائید. *", components=self.bot.components.setup_command())
		except:
			return await check_message.edit("❌ *امکان ارسال پیام به شما وجود ندارد، لطفا محدودیت هارا برداشته یک بار به شخصی ربات پیام بدهید*")

		await check_message.edit("🚀 *برای تغییر تنظیمات گروه به پی وی ربات مراجعه نمائید*")

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

				await render_message.edit(render_chat_info(connection, message.chat))

		connection.close()
		return await render_message.reply("💠 *نغییرات با موفقیت اعمال شد*\nبرای ستاپ دوباره، میتوانید از دستور [/setup](send:/setup) در گروه خود استفاده نمائید")

	async def auto_answer_add(self, message: bale.Message, check_message: bale.Message):
		await check_message.edit(
			"🔷 *ساخت پاسخگوی جدید - مرحله اول*\nلطفا *کلمه* که میخواهید با ارسال آن پاسخی برای کاربر ارسال شود را وارد کنید")
		try:
			se_1: bale.Message = await self.bot.wait_for("message", check = lambda m: m.chat == message.chat and m.author == message.author, timeout = 30.0)
		except asyncio.TimeoutError:
			return await message.chat.send("*عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*\n❓ [دریافت راهنمای این دستور](send:/help_aa_add)")
		else:
			await message.chat.send(
				"🔷 *ساخت پاسخگوی جدید - مرحله دوم*\nلطفا *عبارتی* که میخواهید کاربر با ارسال *{}* آن را دریافت نماید را وارد کنید".format(se_1.content))
			try:
				se_2: bale.Message = await self.bot.wait_for("message", check=lambda
					m: m.chat == message.chat and m.author == message.author, timeout=30.0)
			except asyncio.TimeoutError:
				return await message.chat.send(
					"*عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*\n❓ [دریافت راهنمای این دستور](send:/help_aa_add)")
			else:
				load_msg = await message.chat.send("📡 *در حال برقراری ارتباط با مرکز...*")
				with self.bot.make_db() as connection:
					cursor = connection.cursor()
					cursor.execute("SELECT * FROM auto_answer WHERE word = '{}' AND chat_id = '{}'".format(se_1, message.chat_id))
					if cursor.fetchone():
						return await load_msg.edit("❌ *کلمه {} از قبل در دیتابیس وجود داشته است*".format(se_1.content))

					cursor.execute("INSERT INTO auto_answer(chat_id, word, answer) VALUES (%s, %s, %s)", (message.chat_id, se_1.content, se_2.content))
					connection.commit()

				await load_msg.edit("😉 *پاسخگوی مورد نظر با موفقیت اضافه شد*")

	async def auto_answer_remove(self, message: bale.Message, check_message: bale.Message):
		await check_message.edit(
			"🔷 *حذف پاسخگو*\nلطفا *کلمه* ای را که میخواهید دیگر با ارسال آن پاسخی ارسال نگردد را وارد نمائید")
		try:
			se_1: bale.Message = await self.bot.wait_for("message", check=lambda
				m: m.chat == message.chat and m.author == message.author, timeout=30.0)
		except asyncio.TimeoutError:
			return await message.chat.send(
				"*عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*\n❓ [دریافت راهنمای این دستور](send:/help_aa_remove)")
		else:
			load_msg = await message.chat.send("📡 *در حال برقراری ارتباط با مرکز...*")
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("SELECT * FROM auto_answer WHERE word = '{}' AND chat_id = '{}'".format(se_1, message.chat_id))
				if not cursor.fetchone():
					return await load_msg.edit("❌ *کلمه {} از قبل در دیتابیس وجود نداشته است*".format(se_1.content))

				cursor.execute("DELETE FROM auto_answer WHERE word = '{}' AND chat_id = '{}'".format(se_1.content, message.chat_id))
				connection.commit()

			await load_msg.edit("😉 *پاسخگوی مورد نظر با موفقیت حذف شد*")

