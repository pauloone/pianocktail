import os
import sys
from logging import Handler, LogRecord, basicConfig
from multiprocessing import Event, Process, Queue
from multiprocessing.synchronize import Event as EventType
from queue import Empty


class MultiprocessHandler(Handler):

    def __init__(self, queue: "Queue[str]") -> None:
        super().__init__()
        self._queue = queue

    def emit(self, record: LogRecord) -> None:
        self._queue.put(self.format(record))


def handle_queue(queue: "Queue[str]", stop: EventType, stopped_event: EventType) -> None:
    try:
        os.nice(20)
    except OSError:
        print("Unable to set process niceness")
    while not (stop.is_set() and queue.empty()):
        try:
            record = queue.get(timeout=1e-1)
            sys.stdout.write(record + "\n")
            while True:
                sys.stdout.write(queue.get_nowait() + "\n")
        except Empty:
            pass
        sys.stdout.flush()
    stopped_event.set()


def logger_config(level: int) -> tuple[EventType, EventType]:
    queue: "Queue[str]" = Queue()
    stop_event = Event()
    stopped_event = Event()
    basicConfig(level=level, handlers=[MultiprocessHandler(queue)])

    process = Process(target=handle_queue, args=(queue, stop_event, stopped_event))
    process.start()
    return stop_event, stopped_event
