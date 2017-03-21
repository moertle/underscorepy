
import sys

import _

from . import colors


class Printf(object):
    def __init__(self):
        self.out = sys.stdout
        self._colors = colors.xterm256

    def __call__(self, fmt='', *args):
        self.out.write(fmt % args)
        self.out.flush()
        return self

    def __getitem__(self, name):
        self.out.write(getattr(self._colors, name))
        return self

    def __getattr__(self, name):
        self.out.write(getattr(self._colors, name))
        return self

    def colors(self, name):
        if not hasattr(colors, name):
            raise ValueError
        self._colors = getattr(colors, name)
        return self


class Writeln(Printf):
    def __call__(self, fmt='', *args):
        fmt += self._colors.endl
        return super(Writeln, self).__call__(fmt, *args)


def hexdump(blob, width=16, offset=0):
    fmt = '%%.%dx: ' % len('%.x' % (len(blob) - 1))
    while blob:
        line = bytearray(blob[:width])
        blob = blob[width:]

        _.printf.WHITE(fmt, offset)
        _.printf.CYAN.bright(' '.join('%.2x' % c for c in line))
        _.printf(' ' * ((width-len(line))*3+1))

        for c in line:
            if c < 32 or c > 126:
                _.printf.VIOLET('.')
            else:
                _.printf.WHITE.bright('%c', c)

        _.printf.reset('\n')
        offset += width


_.printf  = Printf()
_.writeln = Writeln()
_.hexdump = hexdump
