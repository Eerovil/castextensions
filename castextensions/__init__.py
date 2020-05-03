import traceback
import json

from .dlna import find_dlna
from .yleareena import YleAreena
from .netflix import Netflix
from .supla import find_supla_program

from .utils.chromecast import Chromecast


def quick_play(cast, app_name, data):
    """
    CAST_APP_SCHEMA = {
        vol.Required('app_name', default=""): cv.string,
        vol.Required('data'): vol.Schema({
            vol.Required("media_id"): cv.string,
            vol.Optional("media_type"): cv.string,
            vol.Optional("enqueue"): cv.boolean,
            vol.Optional("index"): cv.string,
            vol.Optional("extra1"): cv.string,
            vol.Optional("extra2"): cv.string,
        }),
    }
    """
    from pychromecast.controllers.media import MediaController
    from pychromecast.controllers.yleareena import YleAreenaController
    from pychromecast.controllers.supla import SuplaController

    try:
        with open('../config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        with open('../config.json', 'w') as f:
            f.write(json.dumps({
                "areena_key": "",
                "adb_connect": "",
            }, indent=4))

    kwargs = {}

    if app_name == 'dlna':
        controller = MediaController()
        kwargs = {
            'media_url': find_dlna(data.pop('extra1'), data.pop('media_id'),
                                   index=data.pop('index', None)),
            'content_type': data.pop('media_type', None),
        }
    elif app_name == 'yleareena':
        program_id = data.pop('media_id')
        index = data.pop('index', None)
        if data.pop('media_type', None) == 'series':
            areena = YleAreena(config["areena_key"])
            if index == "random":
                program_id = areena.get_series_random_id(program_id)
            else:
                program_id = areena.get_series_latest_id(program_id)
        kaltura_id = YleAreena.get_kaltura_id(program_id)
        controller = YleAreenaController()
        kwargs = {
            'kaltura_id': kaltura_id,
            'audio_language': data.pop('extra1', ''),
            'text_language': data.pop('extra2', 'off'),
        }
    elif app_name == 'supla':
        media_id = data.pop('media_id')

        if data.pop('media_type', None) == 'program':
            media_id = find_supla_program(media_id, match=data.pop('extra2', None))

        controller = SuplaController()
        kwargs = {
            'media_id': media_id,
            'is_live': data.pop('extra1', None),
        }

    # *** Start Special apps not using pychromecast ***
    elif app_name == 'netflix':
        cast = Chromecast(cast)
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
                cast.get_name(), connect_ip=config.get("adb_connect", None)
            )
            netflix.main(data.pop('media_id'))
        except Exception:
            traceback.print_exc()
            cast.quit()
    # *** End Special apps not using pychromecast ***
    else:
        raise NotImplementedError()

    if kwargs:
        cast.wait()
        cast.register_handler(controller)
        controller.quick_play(**kwargs)

    if data:
        controller.logger.warning('Unused data in quick_play: %s', data)
