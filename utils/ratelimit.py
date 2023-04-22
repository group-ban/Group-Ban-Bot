from bale import Message
from datetime import timedelta

class UserRateLimit:
    def __init__(self):
        self.last_message_text = None
        self.last_date = None

    def user_is_rate_limited(self, message: "Message") -> bool:
        if message.message_id == 0:
            return False

        if self.last_date and self.last_date + timedelta(seconds=3) >= message.date and self.last_message_text == message.content:
            self.last_date = message.date
            self.last_message_text = message.content
            return True

        self.last_date = message.date
        self.last_message_text = message.content
        return False