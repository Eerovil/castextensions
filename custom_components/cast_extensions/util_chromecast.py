#! /usr/bin/env python
# -*- coding: utf-8 -*-

from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.const import SERVICE_TURN_OFF
from homeassistant.components.cast.const import SIGNAL_HASS_CAST_APPLICATION

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
        self.hass.services.async_call(
            'media_player', SERVICE_TURN_OFF, {"entity_id": self.entity_id}, blocking=True
        )

    def get_name(self):
        return self.chromecast_name

    def start_app(self, app):
        if app.lower() == 'netflix':
            dispatcher_send(self.hass, SIGNAL_HASS_CAST_APPLICATION,
                            self.entity_id, "start_app", {"app_id": NETFLIX_APP_ID})
        elif app.lower() == 'yleareena':
            dispatcher_send(self.hass, SIGNAL_HASS_CAST_APPLICATION,
                            self.entity_id, "start_app", {"app_id": YLE_AREENA_APP_ID})
        else:
            raise NotImplementedError()

    def quick_play(self, app_name, app_data):
        app_data["app_name"] = app_name
        dispatcher_send(self.hass, SIGNAL_HASS_CAST_APPLICATION,
                        self.entity_id, "quick_play", app_data)


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

    def quick_play(self, app_name, app_data):
        print("MockChromecast: quick_play {} {}".format(app_name, app_data))
