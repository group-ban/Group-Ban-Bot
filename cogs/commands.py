from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
    from ..bot import GroupBan

class Commands:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    @property
    def commands(self):
        return ["/commands", "/groupinfo"]

    def setup(self):
        return {
            self.when_send_command: "message"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content in self.commands:
            return

        if not message.chat.type.is_group_chat():
            return await message.chat.send("❌ *تنها امکان ارسال این دستور در گروه امکان پذیر است*")

        if message.content == "/commands":
            return await message.chat.send("⛏ *دستورات ربات*\n\n💠 *دستورات خدمات اصلی*\n\n🔧 [تنظیم کانفیگ کلی ربات](send:/setup)\n🔧 [تنظیم بخش پاسخگویی خودکار](send:/auto_answer)\n🔧 [تنظیم بخش حذف کلمه](send:/bad_words)\n\n💠 *دستورات خدمات فرعی*\n\n🔧 [دریافت اطلاعات گروه](send:/groupinfo)\n\n💡 برای ارسال دستور، کافیست بر روی آن کلیک نمائید.", components=self.bot.components.site_and_support_buttons())

        elif message.content == "/groupinfo":
            groupinfo = await self.render_chat_info(message.chat)
            return await message.chat.send(groupinfo)

    async def render_chat_info(self, chat: bale.Chat):
        chat = await self.bot.get_chat(chat.chat_id)
        try:
            admins = await chat.get_chat_administrators()
        except:
            admins = None
        return "👥 *اطلاعات اصلی گروه*\n🆔 شناسه عددی: {0}\nℹ نام: {1}\n💎 پرمیوم گروه بان: ندارد\n\n👮‍♂️ *اطلاعات ادمینان گروه*\n{3}\n\n💻 [سایت گروه بان](https://groupban.ir)".format(chat.chat_id, chat.title, chat.invite_link, "\n".join(["👤 {} | {}".format(admin.user.first_name, admin.status.status) for admin in admins]) if admins else "❌ به دلیل کمبود دسترسی، امکان دریافت ادمین هارا ندارم")
