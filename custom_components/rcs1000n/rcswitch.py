import time
import logging

_LOGGER = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    gpio_library = "RPi.GPIO"
except ImportError:
    _LOGGER.warning("No RPi.GPIO available. Using dummy mode.")
    GPIO = None
except RuntimeError:
    _LOGGER.warning("Cannot use RPi.GPIO library (Wrong platform?). Using dummy mode.")
    GPIO = None


class RCSwitch:
    def __init__(self, transmitter_pin):
        self._transmitter_pin = transmitter_pin
        self._repeats = 10
        self._pulse_length = 300

        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(transmitter_pin, GPIO.OUT)
            GPIO.output(transmitter_pin, GPIO.LOW)

    @staticmethod
    def get_code_word_d(s_group, n_channel_code, b_status):
        if not all(ch in '01' for ch in n_channel_code) or len(n_channel_code) != 5:
            raise ValueError("n_channel_code should be a 5-bit binary string")

        if not all(ch in '01' for ch in s_group) or len(s_group) != 5:
            raise ValueError("s_group should be a 5-bit binary string")

        group_code = ''.join('F' if ch == '0' else '0' for ch in s_group)
        channel_code = ''.join('F' if ch == '0' else '0' for ch in n_channel_code)
        status_code = '0F' if b_status else 'F0'

        return group_code + channel_code + status_code

    def send_tri_state(self, s_code_word):
        _LOGGER.debug(f"Code: {s_code_word}")
        for _ in range(self._repeats):
            for c in s_code_word:
                if c == '0':
                    self._send_t0()
                elif c == 'F':
                    self._send_tf()
                elif c == '1':
                    self._send_t1()
            self._send_sync()

    def _send_t0(self):
        self._transmit(1, 3)
        self._transmit(1, 3)

    def _send_t1(self):
        self._transmit(3, 1)
        self._transmit(3, 1)

    def _send_tf(self):
        self._transmit(1, 3)
        self._transmit(3, 1)

    def _send_sync(self):
        self._transmit(1, 31)

    def _transmit(self, n_high_pulses, n_low_pulses):
        for _ in range(n_high_pulses):
            if GPIO:
                GPIO.output(self._transmitter_pin, GPIO.HIGH)
            self._sleep(self._pulse_length / 1000000)

        for _ in range(n_low_pulses):
            if GPIO:
                GPIO.output(self._transmitter_pin, GPIO.LOW)
            self._sleep(self._pulse_length / 1000000)

    @staticmethod
    def _sleep(delay):
        _delay = delay / 100
        end = time.time() + delay - _delay
        while time.time() < end:
            time.sleep(_delay)

