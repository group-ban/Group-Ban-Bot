import asyncio
from typing import TYPE_CHECKING, Optional, List
import bale

if TYPE_CHECKING:
    from ..bot import GroupBan

class Developer:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    @property
    def commands(self):
        return ["/developer", "/d", "/d group list"]

    def setup(self):
        return {
            self.when_send_command: "developer_message"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content in self.commands:
            return

        if message.content == "/d info":
            return await message.chat.send("✨ هویت شما تائید شد؛ شما یکی از توسعه دهندگان گروه بان هستید")

        elif message.content in ["/developer", "d"]:
            return await message.chat.send("✨ *توسعه دهندگان*\n\n⛏ دریافت لیست چت های ثبت شده\n/d group list\n\n⛏ ارسال پیام به چت (الزاما ثبت شده)\n/d group send <chat id>\n\n⛏ دریافت آیدی کاربر (با یکی از پیام های وی)\n/d user get\n\n⛏ بن کردن فرد در گروه خاص (الزاما گروه ثبت شده)\n/d group ban <chat id> <member id>\n\n🚀 گروه بان با شما توسعه دهندگان گرامی، *گـــروه بـــان* شده است.")

        elif message.content == "/d group list":
            with self.bot.make_db() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT chat_id FROM chat LIMIT 100")
                chats = cursor.fetchall()
                return await message.chat.send("💎 *لیست چت ها*\n\n{}".format(f"🔧 {chat_id}" for (chat_id, ) in chats))

        elif message.content.startswith("/d group send "):
            chat_id = "".join(message.content.split(" ")[3::])
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            await message.chat.send("💎 *لطفا تا 30 ثانیه دیگر پیام مورد نظر خود را ارسال کنید*")
            try:
                msg: "bale.Message" = await self.bot.wait_for("developer_message", check = lambda m: m.author == message.author and m.chat == message.chat)
            except asyncio.TimeoutError:
                return message.chat.send("💡 متاستفانه ارسال نکردید")
            else:
                sent_message = await self.bot.send_message(chat_id, msg.content)
                return msg.reply("🚀 *پیام با موفقیت ارسال شد*\n\nپیام با آیدی {0} بر روی سرور های بله و در گروهی با نام مستعار {1} و آیدی {2} قرار گرفت.".format(sent_message.message_id, sent_message.chat.title, sent_message.chat_id))

        elif message.content == "/d user get":
            await message.chat.send("💎 *لطفا تا 30 ثانیه دیگر یک پیام از کاربر مورد نظر ارسال نمائید*")
            try:
                msg: "bale.Message" = await self.bot.wait_for("developer_message", check=lambda m: m.author == message.author and m.chat == message.chat and m.forward_from)
            except asyncio.TimeoutError:
                return message.chat.send("💡 متاستفانه ارسال نکردید")
            else:
                return msg.reply(
                    "🚀 *پیام با موفقیت دریافت شد*\n\nپیام با آیدی {0} بر روی سرور های بله و توسط {1} با آیدی {2} قرار گرفته است.".format(
                        msg.message_id, msg.forward_from.first_name, msg.forward_from.user_id))

        elif message.content.startswith("/d group ban "):
            (chat_id, user_id) = message.content.split(" ")[3::]
            if not chat_id.isdigit():
                return await message.chat.send("❌ *چت آیدی وارد شده نامعتبر است*")

            try:
                await self.bot.ban_chat_member(chat_id, user_id)
            except bale.BaleError as err:
                return await message.chat.send("❌ درخواست انجام نشد\n{}".format(err))
            else:
                return await message.chat.send("🟢 *با موفقیت بن شد*")
    async def render_chat_info(self, chat: bale.Chat, admins: Optional[List["bale.ChatMember"]]):
        chat = await self.bot.get_chat(chat.chat_id)
        return "👥 *مشخصات اصلی گروه*\n\nℹ نام گروه: *{}*\n🆔 شناسه یکتای گروه: *{}*\n💡 این شناسه در هنگام برقراری ارتباط با پشتیبانی گروه بان، خرید پریمیوم ربات و ... کاربرد دارد.\n\n👮‍♂️ *مشخصات ادمینان گروه*\n{}".format(chat.title, chat.chat_id, "\n".join(["👤 {} | {}".format(admin.user.first_name, parse_admin_status(admin.status)) for admin in admins]) if admins else "❌ به دلیل کمبود دسترسی، امکان دریافت ادمین هارا ندارم")
