import time
import logging

_LOGGER = logging.getLogger(__name__)

gpio_library = None

# Try importing RPi.GPIO
try:
    import RPi.GPIO as GPIO
    gpio_library = "RPi.GPIO"
except:
    _LOGGER.warn("No RPi.GPIO available. Using dummy mode!")
    pass

class RCSwitch:
    def __init__(self, transmitter_pin, repeats):
        self._transmitter_pin = transmitter_pin
        self._repeats = repeats
        self._pulse_length = 300

        # setup gpio
        if gpio_library:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(transmitter_pin, GPIO.OUT)
            GPIO.output(transmitter_pin, GPIO.LOW)

    def get_code_word_d(self, s_group, n_channel_code, b_status):
        if not all(ch in '01' for ch in n_channel_code) or len(n_channel_code) > 5:
            raise ValueError("n_channel_code should be a 5-bit binary string")

        if not all(ch in '01' for ch in s_group) or len(s_group) != 5:
            raise ValueError("s_group should be a 5-bit binary string")

        group_code = ''.join('F' if ch == '0' else '0' for ch in s_group)

        channel_code = ''.join('F' if ch == '0' else '0' for ch in n_channel_code)

        status_code = '0F' if b_status else 'F0'

        return group_code + channel_code + status_code + '\0'


    def send_tri_state(self, s_code_word):
        _LOGGER.debug(f"Code: {s_code_word}")
        for _ in range(self._repeats):
            for c in s_code_word:
                if c == '0':
                    self.send_t0()
                elif c == 'F':
                    self.send_tf()
                elif c == '1':
                    self.send_t1()
            self.send_sync()

    def send_t0(self):
        self.transmit(1, 3)
        self.transmit(1, 3)

    def send_t1(self):
        self.transmit(3, 1)
        self.transmit(3, 1)

    def send_tf(self):
        self.transmit(1, 3)
        self.transmit(3, 1)

    def send_sync(self):
        self.transmit(1, 31)



    def transmit(self, n_high_pulses, n_low_pulses):
        for _ in range(n_high_pulses):
            if gpio_library:
                GPIO.output(self._transmitter_pin, GPIO.HIGH)
            time.sleep(self._pulse_length / 1000000)

        for _ in range(n_low_pulses):
            if gpio_library:
                GPIO.output(self._transmitter_pin, GPIO.LOW)
            time.sleep(self._pulse_length / 1000000)

