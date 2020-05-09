"""Component to add new Cast Applications support."""

import traceback
import json
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.components.media_player.const import SERVICE_PLAY_MEDIA
from homeassistant.components.media_player import MEDIA_PLAYER_PLAY_MEDIA_SCHEMA
from homeassistant.helpers.typing import ServiceCallType
from homeassistant.helpers import entity_registry

from .const import DOMAIN

from .app_dlna import find_dlna
from .app_yleareena import YleAreena
from .app_netflix import Netflix
from .app_supla import find_supla_program

from .util_chromecast import ChromecastWrapper


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):

    async def async_quick_play(call: ServiceCallType):
        registry = await entity_registry.async_get_registry(hass)

        for entry in registry.entities.values():
            if entry.entity_id == call.data["entity_id"][0]:
                entity = entry
                break
        else:
            _LOGGER.error('Entity %s not found', call.data["entity_id"][0])
            return

        app_data = json.loads(call.data["media_content_id"])
        app_name = app_data.pop('app_name')

        await hass.async_add_executor_job(
            quick_play,
            hass,
            entity,
            app_name,
            app_data,
            config
        )

    hass.helpers.service.async_register_admin_service(
        DOMAIN,
        SERVICE_PLAY_MEDIA,
        async_quick_play,
        cv.make_entity_service_schema(MEDIA_PLAYER_PLAY_MEDIA_SCHEMA),
    )
    return True


def quick_play(hass, entity, app_name, data, config):
    service_data = {}

    cast_wrapper = ChromecastWrapper(hass, entity)

    _LOGGER.info("Starting quick_play of app %s for chromecast %s",
                 app_name, cast_wrapper.get_name())

    if app_name == 'yleareena':
        program_id = data.pop('media_id')
        index = data.pop('index', None)
        if data.pop('media_type', None) == 'series':
            areena = YleAreena((config['cast_extensions']["areena_key"]))
            if index == "random":
                program_id = areena.get_series_random_id(program_id)
            else:
                program_id = areena.get_series_latest_id(program_id)
        kaltura_id = YleAreena.get_kaltura_id(program_id)
        service_data = {
            'media_id': kaltura_id,
            'audio_lang': data.pop('audio_lang', ''),
            'text_lang': data.pop('text_lang', 'off'),
        }
    elif app_name == 'supla':
        media_id = data.pop('media_id')

        if data.pop('media_type', None) == 'program':
            media_id = find_supla_program(media_id, match=data.pop('title_match', None))

        service_data = {
            'media_id': media_id,
            'is_live': data.pop('is_live', False),
        }
    # *** Start apps using media_player ***
    elif app_name == 'dlna':
        content_type = data.pop('media_type', 'video/mp4')
        media_url = find_dlna(data.pop('dlna_server'), data.pop('media_id'),
                              index=data.pop('index', None), content_type=content_type)
        if not media_url:
            _LOGGER.error("Media not found")
            return
        _LOGGER.info("Playing content %s, %s", media_url, content_type)
        cast_wrapper.play_media(media_url, content_type)

    # *** End apps using media_player ***
    # *** Start Special apps not using pychromecast ***
    elif app_name == 'netflix':
        cast_wrapper.stop()
        cast_wrapper.start_app("netflix")
        try:
            netflix = Netflix(
                entity.original_name, connect_ip=config['cast_extensions'].get("adb_connect", None)
            )
            netflix.main(data.pop('media_id'))
        except Exception:
            traceback.print_exc()
            cast_wrapper.quit()
    # *** End Special apps not using pychromecast ***
    else:
        raise NotImplementedError()

    if service_data:
        cast_wrapper.quick_play(app_name, service_data)

    if data:
        _LOGGER.warning('Unused data in quick_play: %s', data)
