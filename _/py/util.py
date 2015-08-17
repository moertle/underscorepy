
import os
import inspect

def getParent():
    # inspect who called this function
    frames = inspect.getouterframes(inspect.currentframe())
    # get the caller frame
    frame = frames[-1]
    # get the path of the caller
    script = os.path.abspath(frame[1])

    return script
