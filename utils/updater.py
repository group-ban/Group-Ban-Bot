import asyncio
from bale import Updater, Bot

class GroupBanUpdater(Updater):
    def __init__(self, bot: "Bot"):
        super().__init__(bot)

    async def action_getupdates(self):
        while self._is_running:
            try:
                updates = await self.bot.get_updates(offset=self._last_offset)
            except Exception as exc:
                await self.bot.on_error("getUpdates", exc)
            else:
                if updates:
                    for update in updates:
                        await self.call_to_dispatch(update)
                    if self._last_offset:
                        if len(updates) >= 2:
                            self._last_offset = updates[-2 if updates[-1].update_id - updates[-2].update_id <= 20 else -1].update_id + 1
                        else:
                            self._last_offset = updates[-1].update_id if updates[-1].update_id - self._last_offset <= 20 else None
                    else:
                        self._last_offset = updates[-1].update_id + 1

                if self.interval:
                    await asyncio.sleep(self.interval)

    def stop(self):
        if not self._is_running:
            raise RuntimeError("Updater is not running")

        self._is_running = False
