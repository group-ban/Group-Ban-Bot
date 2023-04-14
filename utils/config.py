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

	@property
	def SHELL_CODE(self):
		return self._raw.get("VENV_SHELL_CODE")
