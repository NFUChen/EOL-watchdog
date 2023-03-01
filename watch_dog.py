import time
from watchdog.observers.polling import PollingObserver
from event_handler import EventHandler
from logger import Logger



class WatchDog:
    def __init__(self, watched_path: str, valid_extensions: list[str]) -> None:
        self.valid_extensions = valid_extensions

        self.event_handler = EventHandler(valid_extensions)
        self.observer = PollingObserver()
        
        self.observer.schedule(self.event_handler, watched_path, recursive=True)
        
    def watch(self) -> None:
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            self.observer.stop()
            self.observer.join()
