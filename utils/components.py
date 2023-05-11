from bale import Components as C
from bale import InlineKeyboard

class Components:
    def help_command(self):
        return C(inline_keyboards=[[InlineKeyboard("دعوت ربات به گروه", url="https://groupban.ir/invite"), InlineKeyboard("داکیومنت ربات", url="https://groupban.ir/commands")], [InlineKeyboard("سایت گروه بان", url="https://groupban.ir")]])

    def commands(self):
        return C(inline_keyboards=[[InlineKeyboard("داکیومنت دستورات ربات", url="https://groupban.ir/commands")]])

    def setup_command(self):
        return C(inline_keyboards=[[InlineKeyboard("ضد اسپم", callback_data="anti_spam"), InlineKeyboard("ضد لینک", callback_data="anti_link")], [InlineKeyboard("ضد منشن", callback_data="anti_mention"), InlineKeyboard("ضد کلمه", callback_data="anti_word")], [InlineKeyboard("ضد بازارسال", callback_data="anti_forward"), InlineKeyboard("پاسخگویی خودکار", callback_data="auto_answer")], InlineKeyboard("ذخیره", callback_data="exit")])

    def site_and_support_buttons(self):
        return C(inline_keyboards=[InlineKeyboard("اطلاع رسانی گروه بان", url="https://ble.ir/groupban"), [InlineKeyboard("سایت گروه بان", url="https://groupban.ir/"), InlineKeyboard("پشتیبانی ربات", url="https://groupban.ir/support")]])

    def about_command(self):
        return C(inline_keyboards=[[InlineKeyboard("گیت هاب گروه بان", url="https://groupban.ir/github")], InlineKeyboard("سایت پروژه بله در پایتون (python-bale-bot)", url="https://python-bale-bot.ir")])
