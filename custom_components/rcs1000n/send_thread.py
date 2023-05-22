import threading
import queue
import logging

_LOGGER = logging.getLogger(__name__)

class SendThread(threading.Thread):
    def __init__(self, gpio, repeats):
        super().__init__(daemon=True)
        self._repeats = repeats
        self._gpio = gpio
        self._queue = queue.PriorityQueue()

    def run(self):
        while True:
            try:
                item = self._queue.get()[1]
                item_state = item.get_state()
                # Process the item and its state
                _LOGGER.info("Processing item: %s, state: %s", item, item_state)
            except queue.Empty:
                pass
            except Exception as e:
                _LOGGER.error("Error processing item: %s", e)

    def add_task(self, task):
        for i in range(self._repeats):
            self._queue.put((i, task))
