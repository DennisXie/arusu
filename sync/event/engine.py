from queue import Empty, Queue
from threading import Thread
from time import sleep

from base.event.engine import EVENT_TIMER, Event, BaseEventEngine


class EventEngine(BaseEventEngine):
    def __init__(self, interval: int) -> None:
        super(EventEngine, self).__init__(interval)
        self._thread: Thread = Thread(target=self._run)
        self._timer: Thread = Thread(target=self._run_timer)

    def start(self) -> None:
        """
        Start sync engine to process events and generate timer events.
        """
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self) -> None:
        """
        Stop sync engine.
        """
        self._active = False
        self._timer.join()
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        Put an sync object into sync queue.
        """
        self._queue.put(event)
