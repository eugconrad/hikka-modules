__version__ = (1, 0, 2)

#
#     d88P     d88P          888b    888          888
#      d88P   d88P           8888b   888          888
#       d88P d88P            88888b  888          888
#        d88888P    888888   888Y88b 888  .d88b.  888888
#        d88888P    888888   888 Y88b888 d8P  Y8b 888
#       d88P d88P            888  Y88888 88888888 888
#      d88P   d88P           888   Y8888 Y8b.     Y88b.
#     d88P     d88P          88.8    Y888  "Y8888   "Y888
#
#                      © Copyright 2022
#                    https:// x-net.pp.ua
#
#                 Licensed under the GNU GPLv3
#          https:// www.gnu.org/licenses/agpl-3.0.html
#

# meta developer: @zxcghost666
# requires: HdRezkaApi requests
# scope: hikka_only
# scope: hikka_min 1.2.10

import logging
from HdRezkaApi import *
from telethon import types

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


@loader.tds
class RezkaDLMod(loader.Module):
    """Скачать фильм/сериал с Rezka.ag"""

    strings = {
        "name": "RezkaDL",
        "getting_info": "ℹ️ <b>Loading...</b>",
        "no_args": "⛔️ <b>You must provide a valid link</b>",
    }
    strings_ru = {
        "name": "RezkaDL",
        "getting_info": "ℹ️ <b>Загрузка...</b>",
        "no_args": "⛔️ <b>Необходимо указать корректную ссылку</b>",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    @loader.unrestricted
    async def rezkacmd(self, message: types.Message):
        """<ссылка> - скачать фильм/сериал с Rezka.ag"""
        args = utils.get_args(message)
        args = ["https://rezka.ag/films/action/47246-bystree-puli-2022.html"]   # TODO: Убрать после отладки
        if not args:
            return await utils.answer(message, self.strings("no_args"))

        await utils.answer(message, self.strings("getting_info"))

        try:
            rezka = HdRezkaApi(args[0])
        except Exception as err:
            logger.error(err)
            return await utils.answer(message, self.strings("no_args"))

        is_movie = True if rezka.getType() == "video.movie" else False

        text = "🎞 <b>Фильм:</b> " if is_movie else "🎞 <b>Сериал:</b> "
        text += f'<a href="{rezka.url}">{rezka.name}</a>'
        text += "\n\nℹ️ <i>Выберите озвучку:</i>"

        reply_markup = [[x] for x in [{
            "text": _,
            "callback": self.change_transaltion,
            "args": (rezka, is_movie, _)
        } for _ in rezka.getTranslations()]]
        print(reply_markup)

        await self.inline.form(
            text=text,
            message=message,
            reply_markup=reply_markup,
        )

    async def change_transaltion(
            self,
            call: InlineCall,
            rezka: HdRezkaApi,
            is_movie: bool,
            translation: str,
    ):
        text = "🎞 <b>Фильм:</b> " if is_movie else "🎞 <b>Сериал:</b> "
        text += f'<a href="{rezka.url}">{rezka.name}</a>'
        text += f"\n🎤 <b>Озвучка:</b> {translation}"
        text += "\n\nℹ️ <i>Выберите качество:</i>"
        print(rezka)
        print(rezka.getStream().videos)

        reply_markup = [[x] for x in [{
            "text": _,
            "callback": self.change_resolution,
            "args": (rezka, is_movie, translation, _)
        } for _ in rezka.getStream().videos]]
        print(reply_markup)

        await call.edit(
            text=text,
            reply_markup=reply_markup,
        )

    async def change_resolution(
            self,
            call: InlineCall,
            rezka: HdRezkaApi,
            is_movie: bool,
            translation: str,
            resolution: str,
    ):
        text = "🎞 <b>Фильм:</b> " if is_movie else "🎞 <b>Сериал:</b> "
        text += f'<a href="{rezka.url}">{rezka.name}</a>'
        text += f"\n🎤 <b>Озвучка:</b> {translation}"
        text += f"\n💾 <b>Качество:</b> {resolution}"
        text += "\n\nℹ️ <i>Выберите качество:</i>"
        await call.edit(
            text=text,
        )
