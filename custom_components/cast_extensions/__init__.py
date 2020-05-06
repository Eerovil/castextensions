"""Component to add new Cast Applications support."""

import traceback
import os
import appdirs
import json
import logging
import functools as ft
from pychromecast import get_chromecasts

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

from .util_chromecast import Chromecast


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, config_entry: config_entries.ConfigEntry):
    """Set up Cast from a config entry."""

    async def async_quick_play(call: ServiceCallType):
        registry = await entity_registry.async_get_registry(hass)

        for entry in registry.entities.values():
            if entry.entity_id == call.data["entity_id"][0]:
                chromecast_name = entry.original_name
                break
        else:
            _LOGGER.error('Entity %s not found', call.data["entity_id"][0])
            return

        app_data = json.loads(call.data["media_content_id"])
        app_name = app_data.pop('app_name')

        await hass.async_add_job(
            ft.partial(quick_play, chromecast_name, app_name, app_data, config=config_entry)
        )

    hass.helpers.service.async_register_admin_service(
        DOMAIN,
        SERVICE_PLAY_MEDIA,
        async_quick_play,
        cv.make_entity_service_schema(MEDIA_PLAYER_PLAY_MEDIA_SCHEMA),
    )
    return True


def quick_play(chromecast_name, app_name, data, config: config_entries.ConfigEntry):

    from pychromecast.controllers.media import MediaController
    from pychromecast.controllers.yleareena import YleAreenaController
    from pychromecast.controllers.supla import SuplaController

    kwargs = {}

    cast = Chromecast([cast for cast in get_chromecasts() if cast.device.friendly_name == chromecast_name][0])

    if app_name == 'dlna':
        controller = MediaController()
        kwargs = {
            'media_url': find_dlna(data.pop('dlna_server'), data.pop('media_id'),
                                   index=data.pop('index', None)),
            'content_type': data.pop('media_type', None),
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
        controller = YleAreenaController()
        kwargs = {
            'kaltura_id': kaltura_id,
            'audio_language': data.pop('audio_lang', ''),
            'text_language': data.pop('text_lang', 'off'),
        }
    elif app_name == 'supla':
        media_id = data.pop('media_id')

        if data.pop('media_type', None) == 'program':
            media_id = find_supla_program(media_id, match=data.pop('title_match', None))

        controller = SuplaController()
        kwargs = {
            'media_id': media_id,
            'is_live': data.pop('is_live', None),
        }

    # *** Start Special apps not using pychromecast ***
    elif app_name == 'netflix':
        if cast.running_app == "netflix":
            # TODO: Async needed here. If netflix is running, it needs to be stopped. But
            # chromecast is really slow to first stop an app, then start another one (takes up to
            # 10 seconds). Blocking for 10 seconds here is not something we want, so instead
            # just "quit" netflix by running an empty file.
            cast.play_media("http://localhost")
        else:
            # Start the netflix app, just for show (otherwise chromecast dashboard would load here
            # while we wait: Bad UI)
            cast.start_app("netflix")
        try:
            netflix = Netflix(
                cast.get_name(), connect_ip=config.data.get("adb_connect", None)
            )
            netflix.main(data.pop('media_id'))
        except Exception:
            traceback.print_exc()
            cast.quit()
    # *** End Special apps not using pychromecast ***
    else:
        raise NotImplementedError()

    if kwargs:
        cast.register_handler(controller)
        controller.quick_play(**kwargs)

    if data:
        controller.logger.warning('Unused data in quick_play: %s', data)
