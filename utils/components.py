from bale import Components as C
from bale import InlineKeyboard
from bale import Keyboard

class Components:
    def help_command(self):
        return C(inline_keyboards=[[InlineKeyboard("دعوت ربات به گروه", url="https://groupban.ir/invite"), InlineKeyboard("داکیومنت ربات", url="https://groupban.ir/commands")], [InlineKeyboard("خرید پریمیوم ربات", url="https://groupban.ir/premium"), InlineKeyboard("سفارش تبلیغ", url="https://groupban.ir/tabligh")]])

    def setup_command(self):
        return C(inline_keyboards=[[InlineKeyboard("ضد اسپم", callback_data="anti_spam"), InlineKeyboard("ضد منشن", callback_data="anti_mention")], [InlineKeyboard("ضد لینک", callback_data="anti_link"), InlineKeyboard("ضد کلمه", callback_data="anti_word")], InlineKeyboard("پاسخگویی خودکار", callback_data="auto_answer"), InlineKeyboard("ذخیره", callback_data="exit")])
