import threading
import queue
import logging
from .rcswitch import RCSwitch

_LOGGER = logging.getLogger(__name__)

class SendThread(threading.Thread):
    def __init__(self, gpio, repeats):
        super().__init__(daemon=True)
        self._repeats = repeats

        self._gpio = gpio
        self._queue = queue.PriorityQueue()

        self._rcswitch = RCSwitch(gpio)

    def run(self):
        while True:
            try:
                item = self._queue.get()[2]
                _LOGGER.debug(f"Transmitting {item.get_state()} to socket {item.get_home_code()}-{item.get_plug_code()}")
                self._rcswitch.send_tri_state(self._rcswitch.get_code_word_d(item.get_home_code(), item.get_plug_code(), item.get_state()))
            except queue.Empty:
                pass
            except Exception as e:
                _LOGGER.error("Error processing item: %s", e)

    def add_task(self, task):
        for i in range(self._repeats):
            self._queue.put((i, task._attr_unique_id, task))
