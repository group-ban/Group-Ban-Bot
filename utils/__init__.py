from .components import Components
from .config import ConfigParser
from .ratelimit import UserRateLimit
from farsi_tools import standardize_persian_text as make_persian
from .updater import GroupBanUpdater

persianNumbers = (
	('۱', '1'),
	('۲', '2'),
	('۳', '3'),
	('۴', '4'),
	('۵', '5'),
	('۶', '6'),
	('۷', '7'),
	('۸', '8'),
	('۹', '9'),
	('۰', '0'),
)

messages = {
	"wait": "📡 *در حال برقراری ارتباط با سرور...*\n\n📞 [پشتیبانی ربات](https://groupban.ir/support)",
	"only_group": "❌ *تنها امکان ارسال این دستور در گروه ها امکان پذیر است*",
	"only_pv": "❌ *تنها امکان ارسال این دستور در پیوی ربات امکان پذیر است*",
	"miss_permission": "❌ *برای اجرای این دستور به دسترسی کامل در گروه نیاز است؛ لطفا ربات را ادمین نمائید*",
	"internal_error": "❌ *متاستفیم؛ به دلیل حجم بالای درخواست ها کار در این لحظه متوقف شد، لطفا کمی بعد دوباره تلاش کنید*"
}

__all__ = ("persianNumbers", "Components", "ConfigParser", "make_persian", "UserRateLimit", "GroupBanUpdater", "messages")