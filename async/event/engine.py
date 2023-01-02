import anyio
from anyio import from_thread, to_thread, run, start_blocking_portal, sleep, create_task_group
from asyncio import iscoroutinefunction
from collections import defaultdict

from base.event.engine import BaseEventEngine, Event, EVENT_TIMER, Handler


class EventEngine(BaseEventEngine):
    def __init__(self, interval: int) -> None:
        super(EventEngine, self).__init__(interval)
        self._async_handlers: defaultdict = defaultdict(list)
        self._async_general_handlers: list = []

    def _process(self, event: Event) -> None:
        """
        First distribute sync to those handlers registered listening
        to this type.

        Then distribute sync to those general handlers which listens
        to all types.
        """
        if event.event_type in self._async_handlers:
            [from_thread.run(handler, event) for handler in self._async_handlers[event.event_type]]

        if self._async_general_handlers:
            [from_thread.run(handler, event) for handler in self._async_general_handlers]

        super(EventEngine, self)._process(event)

    async def _run_timer(self) -> None:
        while True:
            await sleep(self._interval)
            event: Event = Event(EVENT_TIMER)
            await self.async_put(event)

    async def start(self) -> None:
        async with create_task_group() as task_group:
            task_group.start_soon(to_thread.run_sync, self._run)
            task_group.start_soon(self._run_timer)

    async def stop(self) -> None:
        self._active = False

    def put(self, event: Event) -> None:
        """
        Put an event into the queue synchronously
        :param event: the event to put
        :return: None
        """
        self._queue.put(event)

    async def async_put(self, event: Event) -> None:
        await to_thread.run_sync(self.put, event)

    def register(self, type: str, handler: Handler) -> None:
        if iscoroutinefunction(handler):
            handler_list: list = self._async_handlers[type]
            if handler not in handler_list:
                handler_list.append(handler)
        else:
            super(EventEngine, self).register(type, handler)

    def unregister(self, type: str, handler: Handler) -> None:
        if iscoroutinefunction(handler):
            handler_list: list = self._async_handlers[type]
            if handler in handler_list:
                handler_list.remove(handler)

            if not handler_list:
                self._async_handlers.pop(type)
        else:
            super(EventEngine, self).unregister(type, handler)

    def register_general(self, handler: Handler) -> None:
        if iscoroutinefunction(handler):
            if handler not in self._async_general_handlers:
                self._async_general_handlers.append(handler)
        else:
            super(EventEngine, self).register_general(handler)

    def unregister_general(self, handler: Handler) -> None:
        if iscoroutinefunction(handler):
            if handler in self._async_general_handlers:
                self._async_general_handlers.remove(handler)
        else:
            super(EventEngine, self).unregister(handler)


if __name__ == "__main__":
    run()
