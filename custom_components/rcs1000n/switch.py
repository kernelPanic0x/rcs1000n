import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
import threading

from .send_thread import SendThread

_LOGGER = logging.getLogger(__name__)

# Constants
DOMAIN = 'rcs1000n'

CONF_GPIO = 'gpio'
CONF_REPEATS = 'repeats'
CONF_SOCKET = 'socket'
CONF_HOME_CODE = 'home_code'
CONF_PLUG_CODE = 'plug_code'
CONF_NAME = 'name'
CONF_UNIQUE_ID = 'unique_id'

# Validate the configuration
SOCKET_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOME_CODE): cv.string,
        vol.Required(CONF_PLUG_CODE): cv.positive_int,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_UNIQUE_ID): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_GPIO): cv.positive_int,
        vol.Required(CONF_REPEATS): cv.positive_int,
        vol.Required(CONF_SOCKET): SOCKET_SCHEMA,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the RCS1000N switch."""
    gpio = config.get(CONF_GPIO)
    repeats = config.get(CONF_REPEATS)
    socket_config = config.get(CONF_SOCKET)

    add_entities([RCS1000NSwitch(gpio, repeats, socket_config)])


class RCS1000NSwitch(SwitchEntity):
    """Representation of a RCS1000N switch."""

    def __init__(self, gpio, repeats, socket_config):
        """Initialize the switch."""
        self._lock = threading.Lock()
        self._gpio = gpio
        self._repeats = repeats
        self._socket_config = socket_config
        self._state = False

        self._send_thread = SendThread(gpio, repeats)
        self._send_thread.start()

    @property
    def name(self):
        """Return the name of the switch."""
        return self._socket_config[CONF_NAME]

    @property
    def unique_id(self):
        """Return a unique ID for the switch."""
        return self._socket_config[CONF_UNIQUE_ID]

    @property
    def is_on(self):
        """Return true if switch is on."""
        with self._lock:
            return self._state

    def get_state(self):
        with self._lock:
            return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        # Implement your code here to control the switch and turn it on
        _LOGGER.info("Turning on RCS1000N switch: %s", self.name)
        with self._lock:
            self._state = True
        self._send_thread.add_task(self)

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        # Implement your code here to control the switch and turn it off
        _LOGGER.info("Turning off RCS1000N switch: %s", self.name)
        with self._lock:
            self._state = False
        self._send_thread.add_task(self)

