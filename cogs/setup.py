from typing import TYPE_CHECKING
import bale
from bale.error import Forbidden

if TYPE_CHECKING:
	from ..bot import GroupBan


class Setup:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	def setup(self):
		return {

		}

	async def when_message(self, message: bale.Message):
		if message.content == "/setup":
			if message.chat.type.is_private_chat():
				return await message.chat.send("🚀 * برای ستاپ کردن من داخل گروه خود، ابتدا من را به آن جا اضافه کرده و سپس برای ستاپ کردن ربات دستور /setup را وارد کنید *")

			return await self.when_send_setup(message)

	async def when_send_setup(self, message: bale.Message):
		check_message = await message.chat.send("📡 * در حال برقراری ارتباط با سرور... *\n😉 لطفا شکیبا باشید")
		try:
			await message.chat.get_chat_administrators()
		except Forbidden:
			return await check_message.edit("❌ *من دسترسی های لازمه را ندارم!*")
		else:
			await message.chat.send("* لطفا پی وی خود را بررسی نمائید *")
			await message.author.send("⚙ * شما میتوانید اطلاعات ربات را بررسی و از طریق دکمه های پنل پایین چت را مدیریت کنید*")
			await message.author.send("🚀 * لطفا خدمت موردنظرتان را از کیبورد زیر انتخاب کنید *")
