from bale import Components as C
from bale import InlineKeyboard

class Components:
    def help_command(self):
        return C(inline_keyboards=[[InlineKeyboard("دعوت ربات به گروه", url="https://groupban.ir/invite"), InlineKeyboard("داکیومنت ربات", url="https://groupban.ir/commands")], [InlineKeyboard("خرید پریمیوم ربات", url="https://groupban.ir/premium"), InlineKeyboard("سفارش تبلیغ", url="https://groupban.ir/tabligh")]])

    def setup_command(self):
        return C(inline_keyboards=[[InlineKeyboard("ضد اسپم", callback_data="anti_spam"), InlineKeyboard("ضد لینک", callback_data="anti_link")], [InlineKeyboard("ضد منشن", callback_data="anti_mention"), InlineKeyboard("ضد کلمه", callback_data="anti_word")], [InlineKeyboard("ضد بازارسال", callback_data="anti_forward"), InlineKeyboard("پاسخگویی خودکار", callback_data="auto_answer")], InlineKeyboard("ذخیره", callback_data="exit")])

    def site_and_support_buttons(self):
        return C(inline_keyboards=[[InlineKeyboard("سایت گروه بان", url="https://groupban.ir/"), InlineKeyboard("پشتیبانی ربات", url="https://groupban.ir/support")]])

    def about_command(self):
        return C(inline_keyboards=[[InlineKeyboard("گیت هاب گروه بان", url="https://github.com/group-ban")], InlineKeyboard("گیت هاب کتابخانه بله بات (python-bale-bot)", url="https://github.com/python-bale-bot")])
