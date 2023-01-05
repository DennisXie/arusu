from collections import defaultdict
from queue import Empty, Queue
from time import sleep
from typing import Callable

EVENT_TIMER = "sync.timer"


class Event(object):
    def __init__(self, event_type: str, data: any = None) -> None:
        self.event_type = type
        self.data = data


Handler = Callable[[Event], None]


class BaseEventEngine(object):
    def __init__(self, interval: int) -> None:
        self._interval = interval
        self._queue = Queue()
        self._active: bool = False
        self._handlers: defaultdict = defaultdict(list)
        self._general_handlers: list = []

    def _run_process_event(self) -> None:
        """
        Get sync from queue and then process it.
        """
        while self._active:
            try:
                event: Event = self._queue.get(block=True, timeout=1)
                self._process_event(event)
            except Empty:
                pass

    def _process_event(self, event: Event) -> None:
        """
        First distribute sync to those handlers registered listening
        to this type.

        Then distribute sync to those general handlers which listens
        to all types.
        """
        if event.event_type in self._handlers:
            [handler(event) for handler in self._handlers[event.event_type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """
        Sleep by interval second(s) and then generate a timer sync.
        """
        while self._active:
            sleep(self._interval)
            event: Event = Event(EVENT_TIMER)
            self.put(event)

    def start(self, *args, **kwargs) -> None:
        """
        Start sync engine to process events and generate timer events.
        """
        pass

    def stop(self) -> None:
        """
        Stop sync engine.
        """
        pass

    def put(self, event: Event) -> None:
        """
        Put an sync object into sync queue.
        """
        pass

    def register(self, type: str, handler: Handler) -> None:
        """
        Register a new handler function for a specific sync type. Every
        function can only be registered once for each sync type.
        """
        handler_list: list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: Handler) -> None:
        """
        Unregister an existing handler function from sync engine.
        """
        handler_list: list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: Handler) -> None:
        """
        Register a new handler function for all sync types. Every
        function can only be registered once for each sync type.
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: Handler) -> None:
        """
        Unregister an existing general handler function.
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)