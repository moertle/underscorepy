
import sys
import os
import inspect
import shlex

import _.py

try:
    import readline
except ImportError:
    sys.stderr.write('Missing readline package\n')
    sys.exit(-1)


class Shell:
    prompt = '->> '

    class Signature:
        def __init__(self, name, func):
            self.func = func
            spec = inspect.getargspec(func.__func__)
            self.positional,self.mapping = spec.args[1:],[]
            if spec.defaults:
                offset = -len(spec.defaults)
                self.positional,self.mapping = self.positional[:offset],self.positional[offset:]
            self.defaults = spec.defaults
            self.varargs = True if spec.varargs else False

    def __init__(self):
        self._signatures = {}
        for name in dir(self):
            if not name.startswith('command_'):
                continue

            func = getattr(self, name)
            name = name[8:]
            sig = Shell.Signature(name, func)
            self._signatures[name] = sig

    def loop(self, intro=None):
        self.old_completer = readline.get_completer()
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')

        try:
            stop = None
            while not stop:
                try:
                    line = input(self.prompt)
                except KeyboardInterrupt:
                    print()
                    continue
                except EOFError:
                    print()
                    break
                try:
                    stop = self.process(line)
                except _.py.error as e:
                    _.writeln.red('[!] %s', e)

        finally:
            readline.set_completer(self.old_completer)

    def process(self, orig):
        _terminal_size = os.get_terminal_size()
        self.rows = _terminal_size.lines
        self.cols = _terminal_size.columns

        line = orig.strip()
        if not line:
            return

        line = shlex.split(line)
        command,line = line[0],line[1:]

        if command not in self._signatures:
            raise _.py.error('Unknown command: %s', command)

        sig = self._signatures[command]

        positional = []
        optional   = []
        varargs    = []

        if sig.defaults:
            optional = list(sig.defaults)

        while line:
            p = line.pop(0)
            if p.startswith('-'):
                p = p[1:]
                try:
                    idx = sig.mapping.index(p)
                except ValueError:
                    raise _.py.error('Unknown argument: -%s', p)
                try:
                    value = line.pop(0)
                except IndexError:
                    raise _.py.error('Missing argument: -%s', p)

                optional[idx] = value
            else:
                if len(positional) < len(sig.positional):
                    positional.append(p)
                else:
                    varargs.append(p)

        if len(positional) < len(sig.positional):
            raise _.py.error('Missing arguments: %s', ' '.join(sig.positional[len(positional):]))

        if not sig.varargs and varargs:
            raise _.py.error('Too many arguments: %s', ' '.join(varargs))

        args = positional + optional + varargs
        sig.func(*args)

    def complete(self, text, state):
        if state == 0:
            self._matches = []
            orig = readline.get_line_buffer()
            line = orig.split()
            position = len(line) or 1
            if line and orig.endswith(' '):
                position += 1

            if position > 1:
                function = getattr(self, 'complete_'+line[0])
            else:
                function = self._complete_commands

            if function:
                self._matches = [m + ' ' for m in function(line, text, position)]

        try:
            return self._matches[state]
        except IndexError:
            return None

    def _complete_commands(self, line, text, position):
        commands = []
        for name in dir(self):
            if name.startswith('command_'):
                name = name[8:]
                if name.startswith(text.lower()):
                    commands.append(name)
        return commands
