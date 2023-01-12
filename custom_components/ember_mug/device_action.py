"""Provides device actions for Ember Mug."""
from __future__ import annotations

import logging

from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_NAME,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_TYPE,
)
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import entity_registry
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, TemplateVarsType
import voluptuous as vol

from .const import DOMAIN, MUG_NAME_REGEX, SERVICE_SET_MUG_NAME

_LOGGER = logging.getLogger(__name__)

ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): SERVICE_SET_MUG_NAME,
        vol.Required(CONF_ENTITY_ID): cv.entity_domain(DOMAIN),
        vol.Required(ATTR_NAME): cv.matches_regex(MUG_NAME_REGEX),
    },
)


async def async_get_actions(
    hass: HomeAssistant,
    device_id: str,
) -> list[dict[str, str]]:
    """List device actions for Ember Mug devices."""
    registry = entity_registry.async_get(hass)
    actions: list[dict[str, str]] = []

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue
        _LOGGER.debug("%s: %s", entry.entity_id, entry)
        actions.append(
            {
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: SERVICE_SET_MUG_NAME,
            },
        )

    return actions


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: TemplateVarsType,
    context: Context | None,
) -> None:
    """Execute a device action."""
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_MUG_NAME,
        {
            ATTR_ENTITY_ID: config[CONF_ENTITY_ID],
            ATTR_NAME: config[ATTR_NAME],
        },
        blocking=True,
        context=context,
    )


async def async_get_action_capabilities(
    hass: HomeAssistant,
    config: ConfigType,
) -> dict[str, vol.Schema]:
    """List action capabilities."""
    fields = {vol.Required(ATTR_NAME): cv.matches_regex(MUG_NAME_REGEX)}

    return {"extra_fields": vol.Schema(fields)}
