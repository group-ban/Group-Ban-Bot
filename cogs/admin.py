from typing import TYPE_CHECKING, Dict, Callable
import bale
import asyncio
if TYPE_CHECKING:
	from ..bot import GroupBan, DB


def render_chat_info(connection: "DB", chat: bale.Chat, more_text = ""):
	render_bool = lambda state: "فعال" if state else "غیر فعال"
	cursor = connection.cursor()
	cursor.execute("SELECT anti_spam, anti_link, anti_mention, anti_word, anti_forward, auto_answer FROM chat WHERE chat_id = '{}'".format(chat.chat_id))
	result = cursor.fetchone()
	if not result:
		return
	(anti_spam, anti_link, anti_mention, anti_word, anti_forward, auto_answer) = result

	return "💠 *ستاپ کردن ربات در گروه {}*\nشناسه یکتا گروه: {}\n\n👥 *اطلاعات گروه*\n🔧 ضد اسپم: {}\n🔧 ضد لینک: {}\n🔧 ضد منشن: {}\n🔧 ضد کلمه: {}\n🔧 ضد بازارسال: {}\n🔧 وضعیت پاسخگویی خودکار: {}".format(
		chat.title,
		chat.chat_id,
		render_bool(anti_spam),
		render_bool(anti_link),
		render_bool(anti_mention),
		render_bool(anti_word),
		render_bool(anti_forward),
		render_bool(auto_answer)
	) + more_text


class Admin:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	@property
	def commands(self) -> Dict[str, Callable]:
		return {"/setup": self.group_setup, "/auto_answer": self.auto_answer, "/auto-answer": self.auto_answer,
			"/aa": self.auto_answer, "/aa toggle": self.auto_answer_toggle, "/aa add": self.auto_answer_add, "/aa remove": self.auto_answer_remove,
			"/anti_word": self.anti_word, "/anti-word": self.anti_word, "/aw": self.anti_word, "/aw toggle": self.anti_word_toggle, "/aw add": self.anti_word_add,
			"/aw remove": self.anti_word_remove}

	def setup(self):
		return {
			self.when_admin_send_message: "verified_message"
		}

	async def when_admin_send_message(self, message: bale.Message):
		if not message.content in self.commands:
			return

		if not message.chat.type.is_group_chat():
			return await message.chat.send(self.bot.base_messages["only_group"])

		check_message = await message.chat.send(self.bot.base_messages["wait"])
		try:
			member = await self.bot.get_chat_member(message.chat_id, str(message.author.user_id))
		except bale.BaleError:
			return await check_message.edit(self.bot.base_messages["miss_permission"])
		else:
			if member.status.is_member():
				return await check_message.edit("❌ *شما ادمین چت نیستید*")

		return await self.commands.get(message.content)(message, check_message)


	async def group_setup(self, message: bale.Message, check_message: bale.Message):
		connection = self.bot.make_db()

		first_render = render_chat_info(connection, message.chat, "\n\n👇 *شما میتوانید با استفاده از دکمه های پیام زیر، تنظیمات را تغییر دهید.*")
		if not first_render:
			return await check_message.edit("❌ *این چت در دیتابیس یافت نشد؛ لطفا ربات را کیک کرده و دوباره به گروه اضافه کنید*")

		try:
			render_message = await message.author.send(first_render)
			action_message = await message.author.send("🔷 *لطفا بخش مورد نظر خود را از طریق دکمه های زیر انتخاب کنید:*\n\n*☝ شما میتوانید وضعیت فعلی امکانات ربات را به صورت زنده بررسی نمائید. *", components=self.bot.components.setup_command())
		except bale.BaleError:
			return await check_message.edit("❌ *امکان ارسال پیام به شما وجود ندارد، لطفا محدودیت هارا برداشته یک بار به شخصی ربات پیام بدهید*")

		await check_message.edit("🚀 *برای تغییر تنظیمات گروه به پی وی ربات مراجعه نمائید*")

		while 1:
			try:
				action: bale.CallbackQuery = await self.bot.wait_for("callback", check = lambda c: c.user == message.author and c.message.message_id == action_message.message_id, timeout = 60.0)
			except asyncio.TimeoutError:
				await action_message.delete()
				break
			else:
				if action.data == "exit":
					await action_message.delete()
					break

				if not action.data in ["anti_spam", "anti_link", "anti_mention", "anti_word", "anti_forward", "auto_answer"]:
					continue

				cursor = connection.cursor()
				cursor.execute("UPDATE chat SET {0} = !{0} WHERE chat_id = '{1}'".format(
					action.data,
					int(message.chat.chat_id)
				))
				connection.commit()

				await render_message.edit(render_chat_info(connection, message.chat, "\n\n👇 *شما میتوانید با استفاده از دکمه های پیام زیر، تنظیمات را تغییر دهید.*"))

		await render_message.edit(render_chat_info(connection, message.chat))
		connection.close()
		return await render_message.reply("💠 *تغییرات با موفقیت اعمال شد*\nبرای ستاپ دوباره، میتوانید از دستور [/setup](send:/setup) در گروه خود استفاده نمائید")

	async def auto_answer(self, message: bale.Message, check_message: bale.Message):
		render_bool = lambda state: "فعال" if state else "غیر فعال"
		with self.bot.make_db() as connection:
			cursor = connection.cursor()
			cursor.execute("SELECT word, answer FROM auto_answer WHERE chat_id = '{}'".format(message.chat.chat_id))
			result = cursor.fetchall()
			cursor.execute(f"SELECT auto_answer FROM chat WHERE chat_id = '{message.chat_id}'")
			(auto_answer_state,) = cursor.fetchone()
		return await check_message.edit("🤖 *پاسخگویی خودکار*\n{1} وضعیت: *{0}* -  🔐 [{2} سازی](send:/aa toggle)\n\nدر این بخش شما امکان اضافه کردن کلمه یا مجموعه ای از کلمات را دارید، که _کاربران عادی_ با فرستادن آن ها پاسخ های مشخصی را دریافت می نماید.\n```[لیست پاسخگو های فعال]{3}```\n🔧 *دستورات بخش*\n\n➕ دستور اضافه کردن پاسخگو\n[/aa add](send:/aa add)\n➖ دستور پاک کردن پاسخگو\n[/aa remove](send:/aa remove)\n\n💡 برای ارسال دستور، کافیست بر روی آن کلیک نمائید.".format(render_bool(auto_answer_state), "🟢" if auto_answer_state else "🔴", render_bool(not auto_answer_state), "\n".join([f"💬 {word}\n⬅ {answer}" for word, answer in result]) if bool(result) else "❌ *در حال حاضر پاسخگویی در این چت فعال نیست*"))

	async def auto_answer_toggle(self, message: bale.Message, check_message: bale.Message):
		with self.bot.make_db() as connection:
			cursor = connection.cursor()
			cursor.execute("UPDATE chat SET {0} = !{0} WHERE chat_id = '{1}'".format(
				"auto_answer",
				int(message.chat.chat_id)
			))
			cursor.execute(f"SELECT auto_answer FROM chat WHERE chat_id = '{message.chat_id}'")
			(auto_answer_state, ) = cursor.fetchone()
			connection.commit()

		return await check_message.edit("✅ *وضعیت بخش پاسخگویی خودکار با موفقیت به {} تغییر کرد.*".format("فعال" if auto_answer_state else "غیر فعال"))

	async def auto_answer_add(self, message: bale.Message, check_message: bale.Message):
		await check_message.edit(
			"🔷 *ساخت پاسخگوی جدید - مرحله اول*\nلطفا *کلمه* که میخواهید با ارسال آن پاسخی برای کاربر ارسال شود را وارد کنید\n💡 کلمه شما میبایست حداقل *2* کاراکتر و حداکثر *20* کاراکتر داشته باشد\n\n⭕ برای لغو عملیات از عبارت *کنسل* و یا */cancel* استفاده کنید")
		try:
			se_1: bale.Message = await self.bot.wait_for("verified_message", check = lambda m: m.chat == message.chat and m.author == message.author, timeout = 30.0)
		except asyncio.TimeoutError:
			return await message.chat.send("❌ *عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*", components=bale.Components(inline_keyboards=bale.InlineKeyboard("دریافت راهنمای دستورات", url="https://groupban.ir/commands")))
		else:
			await se_1.delete()
			if se_1.content in ["/cancel", "کنسل"]:
				return await message.chat.send("❌ *عملیات توسط شما لغو شد*")
			if not (20 >= len(se_1.content) >= 2):
				return await message.chat.send("❌ *عملیات لغو شد؛ متن شما فاقد موارد خواسته شده بود*")
			await check_message.edit(
				"🔷 *ساخت پاسخگوی جدید - مرحله دوم*\nلطفا *عبارتی* که میخواهید کاربر با ارسال *{}* آن را دریافت نماید را وارد کنید\n💡 عبارت شما میبایست حداقل *2* کاراکتر و حداکثر *60* کاراکتر داشته باشد\n\n⭕ برای لغو عملیات از عبارت *کنسل* و یا */cancel* استفاده کنید".format(se_1.content))
			try:
				se_2: bale.Message = await self.bot.wait_for("verified_message", check=lambda
					m: m.chat == message.chat and m.author == message.author, timeout=30.0)
			except asyncio.TimeoutError:
				return await message.chat.send(
					"*عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*", components=bale.Components(inline_keyboards=bale.InlineKeyboard("دریافت راهنمای دستورات", url="https://groupban.ir/commands")))
			else:
				await se_2.delete()
				if se_2.content in ["/cancel", "کنسل"]:
					return await check_message.edit("❌ *عملیات توسط شما لغو شد*")
				if not (60 >= len(se_2.content) >= 2):
					return await check_message.edit("❌ *عملیات لغو شد؛ متن شما فاقد موارد خواسته شده بود*")
				await check_message.edit(self.bot.base_messages["wait"])
				with self.bot.make_db() as connection:
					cursor = connection.cursor()
					cursor.execute("SELECT * FROM auto_answer WHERE word = '{}' AND chat_id = '{}'".format(se_1.content, message.chat_id))
					if cursor.fetchone():
						return await check_message.edit("❌ *کلمه {} از قبل در دیتابیس وجود داشته است*".format(se_1.content))

					cursor.execute("INSERT INTO auto_answer(chat_id, word, answer) VALUES (%s, %s, %s)", (message.chat_id, se_1.content, se_2.content))
					connection.commit()

				await check_message.edit("😉 *پاسخگوی مورد نظر با موفقیت اضافه شد*")

	async def auto_answer_remove(self, message: bale.Message, check_message: bale.Message):
		await check_message.edit(
			"🔷 *حذف پاسخگو*\nلطفا *کلمه* ای را که میخواهید دیگر با ارسال آن پاسخی ارسال نگردد را وارد نمائید")
		try:
			se_1: bale.Message = await self.bot.wait_for("verified_message", check=lambda
				m: m.chat == message.chat and m.author == message.author, timeout=30.0)
		except asyncio.TimeoutError:
			return await message.chat.send(
				"*عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*")
		else:
			await se_1.delete()
			if se_1.content in ["/cancel", "کنسل"]:
				return await check_message.edit("❌ *عملیات توسط شما لغو شد*")
			await check_message.edit(self.bot.base_messages["wait"])
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("SELECT * FROM auto_answer WHERE word = '{}' AND chat_id = '{}'".format(se_1.content, message.chat_id))
				if not cursor.fetchone():
					return await check_message.edit("❌ *کلمه {} از قبل در دیتابیس وجود نداشته است*".format(se_1.content))

				cursor.execute("DELETE FROM auto_answer WHERE word = '{}' AND chat_id = '{}'".format(se_1.content, message.chat_id))
				connection.commit()

			await check_message.edit("😉 *پاسخگوی مورد نظر با موفقیت حذف شد*")

	async def anti_word(self, message: bale.Message, check_message: bale.Message):
		render_bool = lambda state: "فعال" if state else "غیر فعال"
		with self.bot.make_db() as connection:
			cursor = connection.cursor()
			cursor.execute("SELECT word FROM bad_words WHERE chat_id = '{}'".format(message.chat.chat_id))
			result = cursor.fetchall()
			cursor.execute(f"SELECT anti_word FROM chat WHERE chat_id = '{message.chat_id}'")
			(anti_word_state,) = cursor.fetchone()
		return await check_message.edit("🤖 *ضد کلمه*\n{1} وضعیت: *{0}* -  🔐 [{2} سازی](send:/aw toggle)\n\nدر این بخش شما امکان اضافه کردن کلمه یا مجموعه ای از کلمات را دارید، که در هنگام ارسال این کلمات توسط _کاربران عادی_ پیام ارسال شده از طرف وی پاک خواهد شد.\n\n```[لیست کلمه های محدود شده]{3}```\n\n🔧 *دستورات بخش*\n\n➕ دستور اضافه کردن کلمه بد\n[/aw add](send:/aw add)\n➖ دستور پاک کردن کلمه بد\n[/aw remove](send:/aw remove)\n\n💡 برای ارسال دستور، کافیست بر روی آن کلیک نمائید.".format(render_bool(anti_word_state), "🟢" if anti_word_state else "🔴", render_bool(not anti_word_state), "\n".join([f"⭕ {word}" for (word, ) in result]) if bool(result) else "❌ *در حاضر کلمه ای در چت محدود نشده است*"))

	async def anti_word_toggle(self, message: bale.Message, check_message: bale.Message):
		with self.bot.make_db() as connection:
			cursor = connection.cursor()
			cursor.execute("UPDATE chat SET {0} = !{0} WHERE chat_id = '{1}'".format(
				"anti_word",
				int(message.chat.chat_id)
			))
			cursor.execute(f"SELECT anti_word FROM chat WHERE chat_id = '{message.chat_id}'")
			(anti_word_state, ) = cursor.fetchone()
			connection.commit()

		return await check_message.edit("✅ *وضعیت بخش ضد کلمه با موفقیت به {} تغییر کرد.*".format("فعال" if anti_word_state else "غیر فعال"))

	async def anti_word_add(self, message: bale.Message, check_message: bale.Message):
		await check_message.edit(
			"🔷 *ساخت محدودیت جدید*\nلطفا *کلمه* که میخواهید با ارسال آن پیام پاک شود را وارد کنید\n💡 کلمه شما میبایست حداقل *2* کاراکتر و حداکثر *20* کاراکتر داشته باشد\n\n⭕ برای لغو عملیات از عبارت *کنسل* و یا */cancel* استفاده کنید")
		try:
			word: bale.Message = await self.bot.wait_for("verified_message", check = lambda m: m.chat == message.chat and m.author == message.author, timeout = 30.0)
		except asyncio.TimeoutError:
			return await message.chat.send("❌ *عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*", components=bale.Components(inline_keyboards=bale.InlineKeyboard("دریافت راهنمای دستورات", url="https://groupban.ir/commands")))
		else:
			if word.content in ["/cancel", "کنسل"]:
				return await message.chat.send("❌ *عملیات توسط شما لغو شد*")
			if not (20 >= len(word.content) >= 2):
				return await message.chat.send("❌ *عملیات لغو شد؛ متن شما فاقد موارد خواسته شده بود*")

			load_msg = await message.chat.send(self.bot.base_messages["wait"])
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("SELECT * FROM bad_words WHERE word = '{}' AND chat_id = '{}'".format(word.content, message.chat_id))
				if cursor.fetchone():
					return await load_msg.edit("❌ *کلمه {} از قبل در دیتابیس وجود داشته است*".format(word.content))

				cursor.execute("INSERT INTO bad_words(chat_id, word) VALUES (%s, %s)", (message.chat_id, word.content))
				connection.commit()

			await load_msg.edit("😉 *محدودیت مورد نظر با موفقیت اضافه شد*")

	async def anti_word_remove(self, message: bale.Message, check_message: bale.Message):
		await check_message.edit(
			"🔷 *حذف محدودیت*\nلطفا *کلمه* ای را که میخواهید دیگر با ارسال آن محدودیتی ایجاد نشود را وارد نمائید")
		try:
			word: bale.Message = await self.bot.wait_for("verified_message", check=lambda
				m: m.chat == message.chat and m.author == message.author, timeout=30.0)
		except asyncio.TimeoutError:
			return await message.chat.send(
				"*عملیات لغو شد؛ شما موارد خواسته شده را به موقع ارسال نکردید*")
		else:
			if word.content in ["/cancel", "کنسل"]:
				return await message.chat.send("❌ *عملیات توسط شما لغو شد*")
			load_msg = await message.chat.send(self.bot.base_messages["wait"])
			with self.bot.make_db() as connection:
				cursor = connection.cursor()
				cursor.execute("SELECT * FROM bad_words WHERE word = '{}' AND chat_id = '{}'".format(word.content, message.chat_id))
				if not cursor.fetchone():
					return await load_msg.edit("❌ *کلمه {} از قبل در دیتابیس وجود نداشته است*".format(word.content))

				cursor.execute("DELETE FROM bad_words WHERE word = '{}' AND chat_id = '{}'".format(word.content, message.chat_id))
				connection.commit()

			await load_msg.edit("😉 *محدودیت مورد نظر با موفقیت حذف شد*")
