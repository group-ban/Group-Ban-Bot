from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
    from ..bot import GroupBan

class Commands:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    def setup(self):
        return {
            self.when_send_command: "message"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content in ["/auto_answer", "/auto-answer", "/groupinfo"]:
            return

        if not message.chat.type.is_group_chat():
            return await message.chat.send("❌ *تنها امکان ارسال این دستور در گروه امکان پذیر است*")

        if message.content in ["/auto-answer", "/auto_answer"]:
            return await message.chat.send("💡 *پاسخگویی خودکار*\n```[پاسخگویی خودکار چیست؟]*در این بخش شما امکان اضافه کردن کلمه یا مجموعه ای از کلمات را دارید، که کاربر با فرستادن آن ها پاسخ های مشخصی را دریافت می نماید.*\n✏ مثال\n⬅ دیسکورد\n- دیسکورد ما: https://discord.com/invite/...```➕ *دستور اضافه کردن پاسخگو*\n*/aa-add*\n➖ *دستور پاک کردن پاسخگو*\n*/aa-remove*")

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
