from typing import TYPE_CHECKING, Optional, List
import bale

if TYPE_CHECKING:
    from ..bot import GroupBan

def parse_admin_status(status: bale.ChatMemberStatus):
    if status.is_admin():
        return "ادمین"
    elif status.is_owner():
        return "💎 *سازنده چت*"
    return status

class Commands:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    @property
    def commands(self):
        return ["/commands", "/groupinfo"]

    def setup(self):
        return {
            self.when_send_command: "verified_message"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content in self.commands:
            return

        if not message.chat.type.is_group_chat():
            return await message.chat.send(self.bot.base_messages["only_group"])

        if message.content == "/commands":
            with self.bot.make_db() as connection:
                return await message.chat.send("*⚜ [شروع](send:/help) | منوی دستورات | [درباره گروه بان](send:/about)*\n\n💠 *منوی دستورات*\n\n🔧 [قابلیت های کلی (آنتی اسپم، آنتی کد و ...)](send:/setup)\n🔧 [پنل ویژگی پاسخگویی خودکار](send:/aa)\n🔧 [پنل ویژگی ضد کلمه](send:/aw)\n🔧 [پنل تنظیم خوش آمد گو](send:/w)\n🔧 [دریافت مشخصات گروه](send:/groupinfo)\n\n{}\n💡 برای ارسال دستور، کافیست بر روی آن کلیک نمائید.".format("\n".join(["📺 * تبلیغات - 💎 [رزرو تبلیغات](https://ble.ir/support_groupban) *", self.bot.get_ads(connection)])), components=self.bot.components.commands())

        elif message.content == "/groupinfo":
            try:
                admins = await message.chat.get_chat_administrators()
            except bale.BaleError:
                admins = None
            for admin in admins or []:
                if admin.user.is_bot and self.bot.user != admin.user:
                    await message.chat.send("🛡 *سپر امنیتی گروه بان: استفاده از ربات های ناشناخته*\n\n استفاده از ربات های دیگر و ادمین کردن آن ها موجب *پایین آمدن امنیت گروه* شماست.\n⚔ ربات های ناشناخته سعی در جلب توجهات داشته و در فرصتی مناسب، اقدام به هدف قرار دادن گروه شما به وسیله اسپم و ... میکنند.\n\n💡 پیشنهاد میکنیم حدالمکان از ادمین کردن آن ها *خودداری* نمائید.\n\n💎 با گروه بان، امنیت اعضای گروهتو تضمین کن!")
                    break
            groupinfo = await self.render_chat_info(message.chat, admins)
            return await message.chat.send(groupinfo)

    async def render_chat_info(self, chat: bale.Chat, admins: Optional[List["bale.ChatMember"]]):
        chat = await self.bot.get_chat(chat.chat_id)
        return "👥 *مشخصات اصلی گروه*\n\nℹ نام گروه: *{}*\n🆔 شناسه یکتای گروه: *{}*\n💡 این شناسه در هنگام برقراری ارتباط با پشتیبانی گروه بان، خرید پریمیوم ربات و ... کاربرد دارد.\n\n👮‍♂️ *مشخصات ادمینان گروه*\n{}".format(chat.title, chat.chat_id, "\n".join(["👤 {} | {}".format(admin.user.first_name, parse_admin_status(admin.status)) for admin in admins]) if admins else "❌ به دلیل کمبود دسترسی، امکان دریافت ادمین هارا ندارم")
