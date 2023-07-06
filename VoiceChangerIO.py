"""
                    © Copyright 2023
                    https://izxv.fun
                Licensed under the MPL 2.0
          https://www.mozilla.org/en-US/MPL/2.0/
"""

__version__ = (0, 2, 0)

# meta developer: @eugconrad
# scope: hikka_only

import io
import json
import aiohttp

from pydub import AudioSegment

from .. import loader, utils
from ..inline.types import InlineCall

BASE_URL = "http://api.izxv.fun/vcio/"


@loader.tds
class VoiceChangerIOMod(loader.Module):
    strings = {"name": "<b>VoiceChangerIO</b>"}

    async def vciocmd(self, message):
        """.vcio <reply to audio>
        Применить Voice Effect к голосовому сообщению
        """
        reply = await message.get_reply_message()
        if not reply or not reply.document.mime_type.startswith('audio'):
            await message.edit("[{}] Нужен реплай на голосовое сообщение".format(self.strings['name']))
            return
        await message.edit("[{}] Загрузка эффектов, ожидайте...".format(self.strings['name']))
        api_url = BASE_URL + "getVoiceEffects"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    await message.edit("[{}] Произошла ошибка! Код: {}".format(self.strings['name'], response.status))
                    return
                voice_effects = json.loads(await response.read())
        effects_list = [
            {
                "text": f"{voice_effect['id']}. {voice_effect['title']}",
                "callback": self.apply_voice_effect,
                "args": (message, reply, voice_effect)
            }
            for voice_effect in voice_effects
        ]
        cancel_button = {"text": "Отмена", "callback": self.cancel}
        caption = "[{}] Выберите эффект из списка:".format(self.strings['name'])
        await self.inline.form(
            text=caption,
            message=message,
            reply_markup=utils.chunks(effects_list, 2) + [[cancel_button]],
        )

    @staticmethod
    async def cancel(call: InlineCall):
        await call.delete()

    async def apply_voice_effect(self, call: InlineCall, message, reply, voice_effect):
        await call.edit("[{}] Скачиваем голосовое сообщение...".format(self.strings['name']))
        audio_bytes = io.BytesIO()
        await message.client.download_media(reply.media.document, audio_bytes)
        audio_bytes.seek(0)
        await call.edit("[{}] Применяем эффект <b>{}</b>...".format(self.strings['name'], voice_effect['title']))
        api_url = BASE_URL + f"applyVoiceEffect?effectId={voice_effect['id']}"
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data={'audio_file': audio_bytes}) as response:
                if response.status != 200:
                    await message.edit("[{}] Произошла ошибка! Код: {}".format(self.strings['name'], response.status))
                    return
                await call.edit("[{}] Подготавливаем измененное голосовое сообщение...".format(self.strings['name']))
                au = io.BytesIO(await response.read())
        au.seek(0)
        audio = AudioSegment.from_file(au)
        m = io.BytesIO()
        m.name = "voice.ogg"
        audio.split_to_mono()
        dur = len(audio) / 1000
        audio.export(m, format="ogg", bitrate="64k", codec="libopus")
        m.seek(0)
        await call.edit("[{}] Отправляем...".format(self.strings['name']))
        await message.client.send_file(
            message.to_id, m, reply_to=reply.id, voice_note=True, duration=dur
        )
        await call.delete()
