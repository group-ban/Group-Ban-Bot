from .components import Components
from .config import ConfigParser
from farsi_tools import standardize_persian_text as make_persian

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
}

__all__ = ("persianNumbers", "Components", "ConfigParser", "make_persian")