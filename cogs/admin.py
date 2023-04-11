from typing import TYPE_CHECKING
import bale

if TYPE_CHECKING:
	from ..bot import GroupBan

class Admin:
	def __init__(self, bot: "GroupBan"):
		self.bot = bot

	def setup(self):
		return {

		}