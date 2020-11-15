# Cast Extensions

Home Assistant Extensions to cast to Chromecast programmatically using lots of different apps.


# Installation
1. Download `custom_components/cast_extension` to your `custom_components` directory,.

2. Install androidviewclient manually without unneccessary dependecies:
```
source /srv/homeassistant/bin/activate
pip install setuptools requests
pip install androidviewclient==20.0.0b4 --no-dependencies
```

3. Add configuration, see below.

4. Restart Home Assistant

# Configuration

When the integration is enabled, there is a dialog asking for configuration. These are the keys, in order:
```
cast_extensions:
  connect_ip: 192.168.100.3
  areena_key: *areena-api-keys*
```

## connect_ip
Optional. Adb device IP for remote adb connection

## areena_key
Optional. Yle Areena API key to fetch series episodes. Not needed for single episodes.

# Usage

## Netflix

Netflix requires that you have a spare Android phone to remote control. Enable developer settings, ADB and connect the phone to your Home Assistant device.

media_id must be of the format `https://www.netflix.com/title/{id}`

- `app_name`: `netflix`
- `media_id`: Full URL to Netflix item (Make sure it prompts to open the Netflix app on Android when opened)

```yaml
'cast_netflix_to_my_chromecast':
  alias: Cast netflix to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      media_content_type: cast
      media_content_id: '
        {
          "app_name": "netflix",
          "media_id": "https://www.netflix.com/title/60034572"
        }'
    service: cast_extensions.play_media
```

## Spotify

You will need to fetch your spotify web player cookies to use this extension. Here is a guide: https://github.com/enriquegh/spotify-webplayer-token

- `app_name`: `spotify`
- `media_id`: spotify URI
- `sp_dc`: `sp_dc` cookie
- `sp_key`: `sp_key` cookie

Example config: 

```yaml
'cast_spotify_to_my_chromecast':
  alias: Cast spotify to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      media_content_type: cast
      media_content_id: '
        {
          "app_name": "supla",
          "media_id": "spotify:artist:6TKvvwslcx2bKwiX2aBxbd",
          "sp_dc": "ifuahweilfuhawleifawef",
          "sp_key": "ifuwh49gf3wh409q7283rh0q7829awuf7ao9378fhao9w3ufhao9sduh"
        }'
    service: cast_extensions.play_media
```


## Supla

Supla is extended to support programs. Previously only single episodes could be chosen.

Example config to play the latest `aamulypsy` episode containing `Koko Shitti` in the title.

The media_id for SuomiPop Radio should be 2278513 currently.

- `app_name`: `supla`
- `media_id`: Supla item ID / Supla program URL name

Optional:
- `title_match`: Only match items in a given program containing this string
- `is_live`: Item is a livestream

```yaml
'cast_supla_to_my_chromecast':
  alias: Cast supla to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      media_content_type: cast
      media_content_id: '
        {
          "app_name": "supla",
          "media_id": "aamulypsy",
          "title_match": "Koko Shitti"
        }'
    service: cast_extensions.play_media
```

## DLNA

Example config to play a random video from a dlna server at IP:port `192.168.100.2:1337` with the title matching `Friends`.

- `app_name`: `dlna`
- `media_id`: DLNA media title match regex
- `dlna_server`: Server address "IP:PORT"

Optional:
- `media_type`: Content Type (default: `video/mp4`)
- `index`: Index of matches to play. "random" is allowed as well.

```yaml
'cast_dlna_to_my_chromecast':
  alias: Cast dlna to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      media_content_type: cast
      media_content_id: '
        {
          "app_name": "dlna",
          "media_id": "Friends",
          "index": "random",
          "dlna_server": "192.168.100.2:1337"
        }'
    service: cast_extensions.play_media
```

## Yle Areena

Example config to play a yle areena program.

- `app_name`: `yleareena`
- `media_id`: Areena program id (from the URL)

Optional:
- `media_type`: "series" / empty
- `index`: "random" is allowed. Integer does not work currently.

```yaml
'cast_yleareena_to_my_chromecast':
  alias: Cast yleareena to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      media_content_type: cast
      media_content_id: '
        {
          "app_name": "yleareena",
          "media_id": "1-3260345"
        }'
    service: cast_extensions.play_media
```
