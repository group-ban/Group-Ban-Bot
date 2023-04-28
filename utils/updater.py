import asyncio
from bale import Updater, Bot

class GroupBanUpdater(Updater):
    def __init__(self, bot: "Bot"):
        super().__init__(bot)

    async def action_getupdates(self):
        while self._is_running:
            try:
                updates = await self.bot.get_updates(offset=self._last_offset)
                for update in updates:
                    await self.call_to_dispatch(update)

                if bool(updates):
                    if not self._last_offset or ( updates[-1].update_id - self._last_offset <= 50 ):
                        self._last_offset = updates[-1].update_id
                if self.interval:
                    await asyncio.sleep(self.interval)
            except Exception as exc:
                await self.bot.on_error("getUpdates", exc)

    def stop(self):
        if not self._is_running:
            raise RuntimeError("Updater is not running")

        self._is_running = False
