
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
            self.casts = []
            defaults = spec.defaults
            if defaults:
                defaults = list(defaults)
                offset = -len(defaults)
                self.positional,self.mapping = self.positional[:offset],self.positional[offset:]
                while defaults:
                    if not isinstance(defaults[0], type):
                        break
                    name = self.mapping.pop(0)
                    cast = defaults.pop(0)
                    self.casts.append((name,cast))
            self.defaults = defaults
            self.varargs = True if spec.varargs else False

    def __init__(self):
        self._signatures = {}
        for name in dir(self):
            if not name.startswith('shell_'):
                continue
            func = getattr(self, name)
            name = name[6:]
            sig = Shell.Signature(name, func)
            self._signatures[name] = sig

    def loop(self, intro=None):
        self.old_completer = readline.get_completer()
        readline.set_completer_delims(' =#')
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
        command = command.lower()

        if command not in self._signatures:
            raise _.py.error('Unknown command: %s', command)

        sig = self._signatures[command]

        positional = []
        optional   = []
        varargs    = []

        if sig.defaults:
            optional = list(sig.defaults)

        casts = list(sig.casts)
        stop = False
        while line:
            current = line.pop(0)
            if not stop and current.startswith('--'):
                current = current[2:]
                if not current:
                    stop = True
                    continue

                try:
                    idx = sig.mapping.index(current)
                except ValueError:
                    raise _.py.error('Unknown argument: --%s', current)
                try:
                    value = line.pop(0)
                except IndexError:
                    raise _.py.error('Missing argument: --%s', current)

                optional[idx] = value
            else:
                if len(positional) < len(sig.positional):
                    positional.append(current)
                else:
                    if casts:
                        name,cast = casts.pop(0)
                        try:
                            value = cast(current)
                        except:
                            raise _.py.error('Invalid argument for %s: "%s"', cast.__name__, current)
                        positional.append(value)
                    else:
                        varargs.append(current)

        if len(positional) < len(sig.positional):
            missing = sig.positional[len(positional):]
            missing += [n for n,c in casts]
            raise _.py.error('Missing arguments: %s', ' '.join(missing))

        if casts:
            missing = [n for n,c in casts]
            raise _.py.error('Missing arguments: %s', ' '.join(missing))

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
                function = getattr(self, 'complete_'+line[0], None)
                if line[0] in self._signatures:
                    for arg in self._signatures[line[0]].mapping:
                        arg = '--' + arg
                        if arg.startswith(text) and arg not in line:
                            self._matches.append(arg+' ')
            else:
                function = self._complete_shell

            if function:
                for match in function(line, text, position):
                    self._matches.append(match+' ')

        try:
            return self._matches[state]
        except IndexError:
            return None

    def _complete_shell(self, line, text, position):
        commands = []
        for name in dir(self):
            if name.startswith('shell_'):
                name = name[6:]
                if name.startswith(text.lower()):
                    commands.append(name)
        return commands
