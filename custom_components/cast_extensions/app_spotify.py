import spotify_token as st
import spotipy
import time
import json
import logging

_LOGGER = logging.getLogger(__name__)


def get_access_token(sp_dc, sp_key):
    data = st.start_session(sp_dc, sp_key)
    access_token = data[0]
    expires = data[1] - int(time.time())
    return access_token, expires

def play_spotify_media(uri, access_token, device_name):
    client = spotipy.Spotify(auth=access_token)

    counter = 0
    spotify_device_id = None
    while counter < 20:
        devices_available = client.devices()
        for device in devices_available["devices"]:
            if device["name"] == device_name:
                spotify_device_id = device["id"]
                break
        if spotify_device_id:
            break

    if not spotify_device_id:
        _LOGGER.error("Timed out waiting for spotify device %s.", device_name)
        _LOGGER.error("Known devices: %s.", devices_available)
        return

    # Parse uri (allow sending JSON formatted list)
    try:
        json_media = json.loads(uri)
        if not isinstance(json_media, list):
            uri = [json_media]
    except json.JSONDecodeError:
        _LOGGER.debug("Not a JSON formatted string: %s", uri)
        uri = [uri]

    if uri[0].find("track") > 0:
        client.start_playback(device_id=spotify_device_id, uris=uri)
    else:
        client.start_playback(device_id=spotify_device_id, context_uri=uri[0])
