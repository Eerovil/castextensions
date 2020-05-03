# Cast Extensions

Home Assistant Extensions to cast to Chromecast programmatically using lots of different apps.


# Installation

```
pip install https://github.com/Eerovil/castextensions/archive/master.zip
```

# Configuration

`config.json` contains the configuration. Example config:
```
"connect_ip": "192.168.100.3",
"areena_key": "*areena-api-keys*"
```

## connect_ip
Optional. Adb device IP for remote adb connection

## areena_key
Optional. Yle Areena API key to fetch series episodes. Not needed for single episodes.

# Usage

# Schema table

| app_name | media_id | media_type | enqueue | index | extra1 | extra2 |
|----------|----------|------------|---------|-------|--------|--------|
| netflix | Full URL to title (Should prompt to open Netflix on Android) * | | | | | |
| supla | Audio ID / Program name * | "program" | | | *title regex* | |
| dlna | Media item title regex * | *content_type* | | *integer* / "random" | DLNA server ip:port * | |
| yleareena | Areena program / series ID * | "random" | | "random" | | |

## Netflix

Netflix requires that you have a spare Android phone to remote control. Enable developer settings, ADB and connect the phone to your Home Assistant device.

media_id must be of the format `https://www.netflix.com/title/{id}`

```yaml
'cast_netflix_to_my_chromecast':
  alias: Cast netflix to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      app_name: netflix
      data:
        media_id: https://www.netflix.com/title/60034572
    service: cast.cast_app
```

## Supla

Supla is extended to support programs. Previously only single episodes could be chosen.

Example config to play the latest `aamulypsy` episode containing `Koko Shitti` in the title.

The media_id for suomipop should be 2278513 currently.

```yaml
'cast_supla_to_my_chromecast':
  alias: Cast supla to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      app_name: supla
      data:
        media_id: aamulypsy
        media_type: program
        extra1: Koko Shitti
    service: cast.cast_app
```

## DLNA

Example config to play a random video from a dlna server at IP:port `192.168.100.2:1337` with the title matching `Friends`.

```yaml
'cast_dlna_to_my_chromecast':
  alias: Cast dlna to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      app_name: dlna
      data:
        media_id: Friends
        media_type: "video/mp4"
        index: random
        extra1: 192.168.100.2:1337
    service: cast.cast_app
```

## Yle Areena

Example config to play a yle areena program.

```yaml
'cast_yle_areena_to_my_chromecast':
  alias: Cast Yle Areena to My Chromecast
  sequence:
  - data:
      entity_id: media_player.my_chromecast
      app_name: yleareena
      data:
        media_id: "1-3260345"
    service: cast.cast_app
```
