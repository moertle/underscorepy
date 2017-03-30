
def singleton(cls):
    def __init__(self, cls):
        self.cls      = cls
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance == None:
            self.instance = self.cls(*args ,**kwds)
        return self.instance
