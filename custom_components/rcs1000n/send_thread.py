import threading
import queue
import logging
from .rcswitch import RCSwitch

_LOGGER = logging.getLogger(__name__)

class SendThread(threading.Thread):
    def __init__(self, gpio, repeats, home_code, plug_code):
        super().__init__(daemon=True)
        self._repeats = repeats
        self._home_code = home_code
        self._plug_code = plug_code

        self._gpio = gpio
        self._queue = queue.PriorityQueue()

        self._rcswitch = RCSwitch(gpio, repeats)

    def run(self):
        while True:
            try:
                item = self._queue.get()[1]
                self._rcswitch.send_tri_state(self._rcswitch.get_code_word_d(self._home_code, self._plug_code, item.get_state()))
            except queue.Empty:
                pass
            except Exception as e:
                _LOGGER.error("Error processing item: %s", e)

    def add_task(self, task):
        for i in range(self._repeats):
            self._queue.put((i, task))
