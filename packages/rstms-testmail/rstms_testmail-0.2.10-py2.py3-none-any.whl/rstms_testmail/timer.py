import threading
import time


class RepeatedTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.thread = None
        self.stop_event = threading.Event()

    def __enter__(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        self.thread.join()

    def run(self):
        while not self.stop_event.is_set():
            self.function(*self.args, **self.kwargs)
            time.sleep(self.interval)
