#!/usr/bin/env python3

import sys
import time

import _.shell


class Example(_.shell.Shell):
    # called from the _.shell.Shell
    def initialize(self, color):
        self.color = color

    # override the prompt via property to dynamically set it to the current time
    @property
    def prompt(self):
        return time.ctime() + ' > '

    # single command with no arguments, shows the dimensions of the console
    def shell_simple(self):
        _.writeln.bright[self.color]('SIMPLE: %dx%d', self.cols, self.rows)

    # take one argument but only accept integers
    def shell_cast(self, number=int):
        _.writeln.under[self.color]('CAST: %d', number * 10)

    # take one argument but pass in the value into the __init__ function of the class
    def shell_color(self, color=_.colors.xterm256):
        'set the display color'
        self.color = color._name

    # enable tab completion of all possible color values
    def complete_color(self, line, text, position):
        #text = text.lower()
        colors = dir(_.colors.xterm256)
        return [c + ' ' for c in colors if not c.startswith('_') and c.startswith(text)]

    # when
    def shell_flags(self, plain=None, number=10, floating_point=12.34, enable1=True, enable2=False):
        _.writeln[self.color]('--plain          = %s', plain         )
        _.writeln[self.color]('--number         = %s', number        )
        _.writeln[self.color]('--floating-point = %s', floating_point)
        _.writeln[self.color]('--no-enable1     = %s', enable1       )
        _.writeln[self.color]('--enable2        = %s', enable2       )

    class parent_action:
        'Example parent class'

        def __init__(self):
            self.bgcolor = 'BG_BLUE'

        def shell_subcmd(self, name):
            'example of a child command'
            _.writeln[self.bgcolor](' parent class subcmd: %s ', name)

        def complete_subcmd(self, line, text, position):
            names = 'Michael','Matthew','Malcom','Mitch'
            return [n + ' ' for n in names if n.startswith(text)]


shell = Example('yellow')
shell.set_history_file('~/.example.history')
onecmd = ' '.join(sys.argv[1:])
if onecmd:
    try:
        shell.process(onecmd)
    except _.error as e:
        _.writeln.red('%s', e)
else:
    shell.loop()
