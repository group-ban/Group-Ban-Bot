from bale import Components as C
from bale import InlineKeyboard
from bale import Keyboard

class Components:
    def help_command(self):
        return C(keyboards=[[Keyboard("چت های من")], [Keyboard("خرید پریمیوم ربات"), Keyboard("پشتیبانی")], [Keyboard("راهنما")]])