import logging
from homeassistant.const import CONF_SWITCHES
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
CONF_SOCKETS = 'sockets'
CONF_HOME_CODE = 'home_code'
CONF_PLUG_CODE = 'plug_code'
CONF_NAME = 'name'
CONF_UNIQUE_ID = 'unique_id'



# Update SOCKET_SCHEMA to use binary_code_validator for CONF_HOME_CODE and CONF_PLUG_CODE
SOCKET_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOME_CODE): cv.matches_regex("^[01]{5}$"),
        vol.Required(CONF_PLUG_CODE): cv.matches_regex("^[01]{5}$"),
        vol.Required(CONF_NAME): cv.string,
    }
)

# Adjust the validation schema to expect a list of socket configurations.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_GPIO): cv.positive_int,
        vol.Required(CONF_REPEATS): cv.positive_int,
        vol.Required(CONF_SOCKETS): vol.All(cv.ensure_list, [SOCKET_SCHEMA]),
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the RCS1000N switch."""
    gpio = config.get(CONF_GPIO)
    repeats = config.get(CONF_REPEATS)
    socket_configs = config.get(CONF_SOCKETS)
    
    send_thread = SendThread(gpio, repeats)
    send_thread.daemon = True
    send_thread.start()
    
    switches = [RCS1000NSwitch(send_thread, gpio, repeats, socket_config) for socket_config in socket_configs]

    add_entities(switches)


class RCS1000NSwitch(SwitchEntity):
    """Representation of a RCS1000N switch."""

    def __init__(self, send_thread, gpio, repeats, socket_config, resend_interval=60):
        """Initialize the switch."""
        self._lock = threading.Lock()
        self._send_thread = send_thread
        self._gpio = gpio
        self._repeats = repeats
        self._socket_config = socket_config
        self._state = False
        self._resend_interval = resend_interval  # Interval for resending state

        self._name = socket_config[CONF_NAME]
        self._home_code = socket_config[CONF_HOME_CODE]
        self._plug_code = socket_config[CONF_PLUG_CODE]
        self._attr_unique_id = f"{self._home_code}_{self._plug_code}_{self._name}"

        # Start the resend_state function
        self.resend_state()

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        with self._lock:
            return self._state

    def get_state(self):
        with self._lock:
            return self._state

    def get_home_code(self):
        return self._home_code

    def get_plug_code(self):
        return self._plug_code

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

    def resend_state(self):
        """Resend the current state of the switch and schedule the next resend."""
        _LOGGER.info("Resending state of RCS1000N switch: %s", self.name)
        self._send_thread.add_task(self)

        # Schedule the next resend
        timer = threading.Timer(self._resend_interval, self.resend_state)
        timer.daemon = True
        timer.start()

