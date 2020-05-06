"""Adds config flow for Cast extensions."""
from homeassistant import config_entries

import voluptuous as vol

from .const import (  # pylint: disable=unused-import
    CONF_ADB_CONNECT,
    CONF_YLEAREENA_KEY,
    DOMAIN,
)


class CastExtensionsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title='Cast Extensions', data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Optional(CONF_ADB_CONNECT): str,
                vol.Optional(CONF_YLEAREENA_KEY): str,
            })
        )
