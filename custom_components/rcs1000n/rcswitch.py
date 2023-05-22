import time

gpio_library = None

# Try importing RPi.GPIO
try:
    import RPi.GPIO as GPIO
    gpio_library = "RPi.GPIO"
except:
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
        n_return_pos = 0
        s_return = [''] * 13

        if n_channel_code < 1 or n_channel_code > 31:
            s_return[0] = ''
            return s_return

        for i in range(5):
            if s_group[i] == '0':
                s_return[n_return_pos] = 'F'
            elif s_group[i] == '1':
                s_return[n_return_pos] = '0'
            else:
                s_return[0] = ''
                return s_return
            n_return_pos += 1

        str_bin = bin(n_channel_code)[2:].zfill(5)  # Convert to binary with leading zeros
        for i in range(len(str_bin)):
            if str_bin[i] == '0':
                s_return[n_return_pos] = 'F'
            elif str_bin[i] == '1':
                s_return[n_return_pos] = '0'
            n_return_pos += 1

        if b_status:
            s_return[n_return_pos] = '0'
            s_return[n_return_pos + 1] = 'F'
        else:
            s_return[n_return_pos] = 'F'
            s_return[n_return_pos + 1] = '0'

        s_return[n_return_pos + 2] = ''
        return s_return

    def send_tri_state(self, s_code_word):
        for n_repeat in range(self._repeats):
            i = 0
            while s_code_word[i] != '':
                if s_code_word[i] == '0':
                    self.send_t0()
                elif s_code_word[i] == 'F':
                    self.send_tf()
                elif s_code_word[i] == '1':
                    self.send_t1()
                i += 1
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
        for i in range(n_high_pulses):
            if gpio_library:
                GPIO.output(self._transmitter_pin, GPIO.HIGH)
            time.sleep(self._pulse_length / 1000000)

        for i in range(n_low_pulses):
            if gpio_library:
                GPIO.output(self._transmitter_pin, GPIO.LOW)
            time.sleep(self._pulse_length / 1000000)

