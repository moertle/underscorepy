
import _

class Audio:
    device:    str = _.records.data.primary_key()
    frequency: int
    bits:      int
    samples:   int


@_.records.data.ignore
class Ignore:
    test: int = _.records.data.primary_key()
