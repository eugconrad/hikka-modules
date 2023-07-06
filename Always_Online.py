"""
                    © Copyright 2023
                    https://izxv.fun
                Licensed under the MPL 2.0
          https://www.mozilla.org/en-US/MPL/2.0/
"""

__version__ = (0, 1, 0)

# meta developer: @eugconrad
# scope: hikka_only

import datetime
import logging

from telethon import types, functions
from telethon.tl.types import UpdateUserStatus

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class AlwaysOnlineMod(loader.Module):
    """Вечный онлайн"""

    strings = {"name": "AlwaysOnline"}
    strings_ru = {"_cls_doc": "Вечный онлайн"}
    last_online = 0
    per = 2 * 60 - 10

    async def client_ready(self, client, db) -> None:
        self.client = client
        self.me = await client.get_me()
        self.uid = self.me.id
        self.chat, _ = await utils.asset_channel(
            client, "[Вечный онлайн]",
            "Этот чат необходим для работы вечного онлайна",
            channel=False, silent=True, archive=True
        )

    async def go_online(self, now = None):
        if now is None:
            now = datetime.datetime.now()
        await self.client.send_message(
            self.chat,
            f'<emoji document_id="5818967120213445821">🛡</emoji> <b>Вышли в онлайн</b>\n'
            f'<emoji document_id="5818865088970362886">❕</emoji> '
            f'<code>{now.strftime("%H:%M:%S.%f")[:-3]}</code>'
        )
        await self.client(functions.account.UpdateStatusRequest(offline=False))
        self.last_online = now.timestamp()
        return now

    async def alonlinecmd(self, message: types.Message):
        """ Проверка работоспособности модуля """
        await utils.answer(message, "Все работает!")

    @loader.loop(interval=1, autostart=True, wait_before=True)
    async def scheduler(self) -> None:
        if self.last_online != 0 and self.last_online + self.per <= datetime.datetime.now().timestamp():
            await self.go_online()
            # logger.info('Вышли в онлайн через go_online()')

    @loader.raw_handler(UpdateUserStatus)
    async def update_handler(self, update: UpdateUserStatus):

        if update.user_id == self.uid and type(update.status) == types.UserStatusOffline:
            await self.go_online()
            # logger.info('Пользователь вышел в оффлайн')

        elif update.user_id == self.uid and type(update.status) == types.UserStatusOnline:
            self.last_online = 0
            # logger.info('Пользователь вышел в онлайн')

