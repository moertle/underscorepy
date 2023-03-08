
import _

class Audio:
    device:    str = _.records.dataclass.primary_key()
    frequency: int
    bits:      int
    samples:   int


@_.records.dataclass.ignore
class Ignore:
    test: int = _.records.dataclass.primary_key()
