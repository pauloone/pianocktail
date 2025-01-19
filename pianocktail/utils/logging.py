import sys
import os
from queue import Empty
from multiprocessing import Process, Queue, Event
from multiprocessing.synchronize import Event as EventType
from logging import Handler, LogRecord, root, basicConfig, DEBUG

class MultiprocessHandler(Handler):

    def __init__(self, queue: Queue):
        super().__init__()
        self._queue = queue

    def emit(self, record: LogRecord) -> None:
        self._queue.put(self.format(record))

def handle_queue(queue: Queue, stop: EventType):
    try:
        os.nice(20)
    except OSError:
        print("Unable to set process niceness")
    while(True):
        try:
            record=queue.get(timeout=1)
            sys.stdout.write(record + '\n')
            while True:
                sys.stdout.write(queue.get_nowait() + '\n')
        except Empty:
            pass
        sys.stdout.flush()
        if stop.is_set():
            return

def logger_config() -> EventType:
    queue = Queue()
    stop_event = Event()
    basicConfig(level=DEBUG, handlers=[MultiprocessHandler(queue)])

    process = Process(target=handle_queue, args=(queue, stop_event))
    process.start()
    return stop_event