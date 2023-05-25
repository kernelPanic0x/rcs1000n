import threading
import queue
import logging
from .rcswitch import RCSwitch

_LOGGER = logging.getLogger(__name__)

class SendThread(threading.Thread):
    def __init__(self, gpio, repeats):
        super().__init__(daemon=True)
        self.repeats = repeats
        self.queue = queue.PriorityQueue()
        self.rcswitch = RCSwitch(gpio)

    def run(self):
        while True:
            try:
                _, _, item = self.queue.get()
                state = item.get_state()
                home_code = item._home_code
                plug_code = item._plug_code
                _LOGGER.debug(f"Transmitting {state} to socket {home_code}-{plug_code}")
                code_word = self.rcswitch.get_code_word_d(home_code, plug_code, state)
                self.rcswitch.send_tri_state(code_word)
            except queue.Empty:
                pass
            except Exception as e:
                _LOGGER.error("Error processing item: %s", e)

    def add_task(self, task):
        for i in range(self.repeats):
            unique_id = task._attr_unique_id
            self.queue.put((i, unique_id, task))

