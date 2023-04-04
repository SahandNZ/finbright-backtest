class Event:
    def __init__(self):
        self.__event_handlers = []

    def add_handler(self, handler):
        self.__event_handlers.append(handler)
        return self

    def remove_handler(self, handler):
        self.__event_handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for event_handler in self.__event_handlers:
            event_handler(*args, **kwargs)
