"""Test component setup."""
from homeassistant.config_entries import SOURCE_BLUETOOTH
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    UnitOfTemperature,
)
from homeassistant.data_entry_flow import FlowResultType
import pytest
from voluptuous import MultipleInvalid

from tests import MUG_SERVICE_INFO, TEST_MAC, TEST_MUG_NAME, patch_async_setup_entry


async def test_bluetooth_discovery(hass):
    """Test discovery via bluetooth with a valid device."""
    result = await hass.config_entries.flow.async_init(
        "ember_mug",
        context={"source": SOURCE_BLUETOOTH},
        data=MUG_SERVICE_INFO,
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with pytest.raises(MultipleInvalid):
        with patch_async_setup_entry() as mock_setup_entry:
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {},
            )
        await hass.async_block_till_done()

    with patch_async_setup_entry() as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_ADDRESS: TEST_MAC,
                CONF_NAME: TEST_MUG_NAME,
            },
        )
    await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == TEST_MUG_NAME
    assert result["data"] == {
        CONF_ADDRESS: TEST_MAC,
        CONF_NAME: TEST_MUG_NAME,
        CONF_TEMPERATURE_UNIT: UnitOfTemperature.CELSIUS,
    }

    assert len(mock_setup_entry.mock_calls) == 1
