from bale import Components as C
from bale import InlineKeyboard
from bale import Keyboard

class Components:
    def help_command(self):
        return C(keyboards=[[Keyboard("چت های من")], [Keyboard("خرید پریمیوم ربات"), Keyboard("پشتیبانی")], [Keyboard("راهنما")]])

    def setup_command(self):
        return C(inline_keyboards=[[InlineKeyboard("ضد اسپم", callback_data="anti_spam"), InlineKeyboard("ضد منشن", callback_data="anti_mention")], [InlineKeyboard("ضد لینک", callback_data="anti_link"), InlineKeyboard("ضد کلمه", callback_data="anti_word")], InlineKeyboard("پاسخگویی خودکار", callback_data="auto_answer"), InlineKeyboard("ذخیره", callback_data="exit")])
