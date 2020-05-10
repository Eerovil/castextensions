#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_MEDIA_STOP
from homeassistant.components.media_player.const import SERVICE_PLAY_MEDIA

YLE_AREENA_APP_ID = 'A9BCCB7C'
NETFLIX_APP_ID = 'CA5E8412'


class ChromecastWrapper():
    """
    Helper class, which is basically the same as pychromecast.Chromecast
    """
    def __init__(self, hass, entity):
        self.hass = hass
        self.chromecast_name = entity.original_name
        self.entity_id = entity.entity_id

    def quit(self):
        self.hass.services.call(
            'media_player', SERVICE_TURN_OFF, {"entity_id": self.entity_id}, blocking=True
        )

    def stop(self):
        self.hass.services.call(
            'media_player', SERVICE_MEDIA_STOP, {"entity_id": self.entity_id}, blocking=True
        )

    def get_name(self):
        return self.chromecast_name

    def start_app(self, app):
        if app.lower() == 'netflix':
            app_id = NETFLIX_APP_ID
        elif app.lower() == 'yleareena':
            app_id = YLE_AREENA_APP_ID
        else:
            raise NotImplementedError()
        self.hass.services.call(
            'media_player', SERVICE_PLAY_MEDIA, {
                "entity_id": self.entity_id,
                "media_content_id": json.dumps({"app_id": app_id}),
                "media_content_type": "cast"
            }, blocking=True
        )

    def play_media(self, url, content_type="video/mp4"):
        self.hass.services.call(
            'media_player', SERVICE_PLAY_MEDIA, {
                "entity_id": self.entity_id,
                "media_content_id": url,
                "media_content_type": content_type
            }, blocking=True
        )

    def quick_play(self, app_name, app_data):
        app_data["app_name"] = app_name
        self.hass.services.call(
            'media_player', SERVICE_PLAY_MEDIA, {
                "entity_id": self.entity_id,
                "media_content_id": json.dumps(app_data),
                "media_content_type": "cast"
            }, blocking=True
        )


class MockChromecast(ChromecastWrapper):
    """
    When you're developing and don't really want to cast
    """
    def __init__(self, chromecast_ip):
        pass

    def quit(self):
        print("MockChromecast: quit()")

    def get_name(self):
        return "Mock Chromecast"

    def start_app(self, app):
        if app.lower() == 'netflix':
            print("MockChromecast: start_app {}".format(app))
        elif app.lower() == 'areena':
            print("MockChromecast: start_app {}".format(app))
        else:
            raise NotImplementedError()

    def play_media(self, url, content_type="video/mp4"):
        print("MockChromecast: play_media {} {}".format(url, content_type))

    def quick_play(self, app_name, app_data):
        print("MockChromecast: quick_play {} {}".format(app_name, app_data))
