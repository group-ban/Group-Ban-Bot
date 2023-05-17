from typing import TYPE_CHECKING
import bale
from utils import persianNumbers

if TYPE_CHECKING:
    from ..bot import GroupBan, DB

def render_user_ads(connection: "DB", user: bale.User):
    render_visit = lambda m, n: f"{n}/{m} بار دیده شده" if m > n else f"تبلیغ به تعداد حداکثر ({m}) بار دیده شده"
    cursor = connection.cursor()
    cursor.execute("SELECT name, max_visit_cnt, visit_cnt FROM ads WHERE user_id = '{}'".format(user.user_id))
    result = cursor.fetchall()
    if not bool(result):
        return "❌ * لیست خالی است *"

    text = ""
    for (name, max_visit_cnt, visit_cnt) in result:
        text += f"✨ {name}: {render_visit(max_visit_cnt, visit_cnt)}\n\n"

    for (persian_num, english_num) in persianNumbers:
        text = text.replace(english_num, persian_num)

    return text

class ADS:
    def __init__(self, bot: "GroupBan"):
        self.bot = bot

    @property
    def commands(self):
        return ["/ads", ]

    def setup(self):
        return {
            self.when_send_command: "verified_message",
            self.ads_action: "ads_enter"
        }

    async def when_send_command(self, message: bale.Message):
        if not message.content or not message.content in self.commands or not message.chat.type.is_private_chat():
            return

        if message.content == "/ads":
            with self.bot.make_db() as connection:
                return await self.bot.send_message_without_convert(message.chat_id, "💎 *تبلیغات در گروه بان*\n\n💳 *سفارشات*\n{}\n```[💲 سفارس تبلیغ]💨 *تبلیغات در گروه بان*\nبا تبلیغات گروه ، کانال و یا کسب و کار خود در گروه بان ، کار شما در صد ها گروه پشتیبانی شده توسط گروه بان منتشر و دیده می شود و میتوانید به سریع ترین شکل ممکن جذب خوبی داشته باشید .\n⭕ تبلیغات شما به صورت *تعداد ارسال* محاسبه و *بدون محدودیت زمانی* خواهند بود.\n\n💥 *پلن های تبلیغات*\n💚 پلن یک: ۲۵۰ ارسال ، *ده* هزار تومان\n🧡 پلن دو: ۵۰۰ ارسال ، *شانزده* هزار تومان\n💛 پلن سه: ۱۰۰۰ ارسال ، *بیست و هفت* هزار تومان\n\n💎 *پلن ویژه (ارسال همگانی)*\n💟 ارسال همگانی تبلیغ به *ده* گروه، *سی* هزار تومان\n\n👮‍♂️ در صورت تمایل به خرید، گزارش مشکل و ... با کارشناس مالی مجموعه (@support_groupban2) در تماس باشید.```".format(render_user_ads(connection, message.author)))

    async def ads_action(self, ads_id):
        with self.bot.make_db() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE ads SET visit_cnt = visit_cnt + 1 WHERE ads_id = %s", (ads_id, ))
            connection.commit()
            cursor.close()
