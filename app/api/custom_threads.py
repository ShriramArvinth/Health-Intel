import threading

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self.stop_event = threading.Event()
    
    def stop(self):
        self.stop_event.set()
    
    def is_stopped(self):
        return self.stop_event.is_set()            