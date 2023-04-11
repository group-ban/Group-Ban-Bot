from __future__ import annotations
import json


class ConfigParser:
	def __init__(self, file: str):
		self._raw = json.loads(file)

	@property
	def TOKEN(self):
		return self._raw.get("TOKEN")

	@property
	def DATABASE(self):
		return self._raw.get("DATABASE")

	def get_problem(self, key: str):
		return self._raw.get("HOMEWORKS").get(key)

	def get_counseling(self, key: str):
		return self._raw.get("COUNSELING").get(key)