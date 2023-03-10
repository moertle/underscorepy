
import _

class audio:
    device    : str = _.data.uniq(_.data.pkey())
    frequency : int = 48000
    bits      : int = 16
    samples   : int = _.data.uniq()


@_.data.no_handler
@_.data.no_pkey
class ignored:
    __no_handler = True
    __no_pkey    = True

    test : int = 100
