
import sys

import _

out = sys.stdout


class Colors:
    def black  (self, fmt='', *args): self('\x1b[1;30m' + fmt + '\x1b[0m', *args)
    def red    (self, fmt='', *args): self('\x1b[1;31m' + fmt + '\x1b[0m', *args)
    def green  (self, fmt='', *args): self('\x1b[1;32m' + fmt + '\x1b[0m', *args)
    def yellow (self, fmt='', *args): self('\x1b[1;33m' + fmt + '\x1b[0m', *args)
    def blue   (self, fmt='', *args): self('\x1b[1;34m' + fmt + '\x1b[0m', *args)
    def purple (self, fmt='', *args): self('\x1b[1;35m' + fmt + '\x1b[0m', *args)
    def cyan   (self, fmt='', *args): self('\x1b[1;36m' + fmt + '\x1b[0m', *args)
    def white  (self, fmt='', *args): self('\x1b[1;37m' + fmt + '\x1b[0m', *args)


class Printf(Colors):
    def __call__(self, fmt='', *args):
        out.write(fmt % args)
        out.flush()


class Writeln(Colors):
    def __call__(self, fmt='', *args):
        out.write(fmt % args)
        out.write('\n')


def hexdump(blob, width=16, offset=0):
    fmt = '%%.%dx: ' % len('%.x' % (len(blob) - 1))
    while blob:
        line = blob[:width]
        blob = blob[width:]

        _.printf.white(fmt, offset)
        _.printf.cyan(' '.join('%.2x' % ord(c) for c in line))
        _.printf(' ' * ((width-len(line))*3+1))

        for c in line:
            if ord(c) < 32 or ord(c) > 126:
                _.printf.black('.')
            else:
                _.printf.white('%c', c)

        _.printf('\n')
        offset += width


_.printf  = Printf()
_.writeln = Writeln()
_.hexdump = hexdump
