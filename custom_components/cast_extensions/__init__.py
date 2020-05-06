"""Component to add new Cast Applications support."""

import traceback
import json
import logging

from homeassistant import config_entries
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
    return True


async def async_setup_entry(hass, config_entry: config_entries.ConfigEntry):
    """Set up Cast from a config entry."""

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

        quick_play(hass, entity, app_name, app_data, config=config_entry)

    hass.helpers.service.async_register_admin_service(
        DOMAIN,
        SERVICE_PLAY_MEDIA,
        async_quick_play,
        cv.make_entity_service_schema(MEDIA_PLAYER_PLAY_MEDIA_SCHEMA),
    )
    return True


def quick_play(hass, entity, app_name, data, config: config_entries.ConfigEntry):
    service_data = {}

    cast_wrapper = ChromecastWrapper(hass, entity)

    _LOGGER.info("Starting quick_play of app %s for chromecast %s",
                 app_name, cast_wrapper.get_name())

    if app_name == 'dlna':
        app_name = 'media'
        service_data = {
            'media_id': find_dlna(data.pop('dlna_server'), data.pop('media_id'),
                                  index=data.pop('index', None)),
            'media_type': data.pop('media_type', 'video/mp4'),
        }
    elif app_name == 'yleareena':
        program_id = data.pop('media_id')
        index = data.pop('index', None)
        if data.pop('media_type', None) == 'series':
            areena = YleAreena((config.data["areena_key"]))
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

    # *** Start Special apps not using pychromecast ***
    elif app_name == 'netflix':
        cast_wrapper.quit()
        cast_wrapper.start_app("netflix")
        try:
            netflix = Netflix(
                entity.original_name, connect_ip=config.data.get("adb_connect", None)
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
