
import sys
import os
import inspect
import functools

import _

try:
    import readline
except ImportError:
    sys.stderr.write('Missing readline package\n')
    sys.exit(-1)


class _Signature:
    def __init__(self, func):
        # save a reference to the function
        self.func = func
        # use the built-in python inspector to get the spec
        spec = inspect.getargspec(func.__func__)
        # initially assume any arguments are positional
        self.positional = spec.args[1:]
        self.mapping    = []
        self.casts      = []

        # look at arguments that have a default type or value assigned
        defaults = spec.defaults
        if defaults:
            # convert tuple into modifiable list
            defaults = list(defaults)
            # segment positional arguments from the rest of the function signature
            offset = -len(defaults)
            self.positional,self.mapping = self.positional[:offset],self.positional[offset:]
            # treat optional arguments with a default type as a required positional argument that is cast
            while defaults:
                # stop on first non-type default value
                if not isinstance(defaults[0], type):
                    break
                # remote it from the optional arguments
                name = self.mapping.pop(0)
                cast = defaults.pop(0)
                # and append it to a separate list for casting
                self.casts.append((name,cast))

            # arguments with a boolean default of True get their name inverted
            for idx,default in enumerate(defaults):
                if default is True:
                    self.mapping[idx] = 'no-' + self.mapping[idx]

        # store the remaining default values
        self.defaults = defaults
        # allow commands to take a arbitrary number of arguments
        self.varargs = True if spec.varargs else False


class Shell:
    prompt = '->> '
    true_values  = [ 't', 'true',  'y', 'yes', '1', 'on'  ]
    false_values = [ 'f', 'false', 'n', 'no',  '0', 'off' ]

    def __init__(self):
        self._signatures = {}
        self.__parse_shell_commands(self)

    def __parse_shell_commands(self, obj):
        # iterate over the instance members
        for name in dir(obj):
            # if it is a parent class...
            if name.startswith('parent_'):
                cls = getattr(obj, name)
                if not inspect.isclass(cls):
                    raise _.error('Parent is not a class: %s', name)
                name = name[7:]
                # instantiate an instance
                instance = cls()
                instance._signatures = {}
                obj._signatures[name] = instance
                # recursive call
                self.__parse_shell_commands(instance)
            elif name.startswith('shell_'):
                func = getattr(obj, name)
                name = name[6:]
                obj._signatures[name] = _Signature(func)

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
                except _.error as e:
                    _.writeln.red('[!] %s', e)
        finally:
            readline.set_completer(self.old_completer)

    def process(self, original):
        # strip and split the original input
        line = original.strip().split()
        # do nothing on empty line
        if not line: return

        # preserve parent commands for error message
        parent = []
        # iterate over the signatures tree
        signatures = self._signatures
        while True:
            # pop the
            command = line.pop(0).lower()
            parent.append(command)

            signature = signatures.get(command)
            if not signature:
                raise _.error('Unknown command: %s', ' '.join(parent))

            # is it a signature?
            if isinstance(signature, _Signature):
                break

            # otherwise it is a "parent_" class
            signatures = signature._signatures
            if not line:
                raise _.error('Missing command: %s', ' '.join(parent))

        positional = []
        optional   = []
        varargs    = []

        if signature.defaults:
            optional = list(signature.defaults)

        casts = list(signature.casts)
        stop = False
        while line:
            current = line.pop(0)
            if not stop and current.startswith('--'):
                current = current[2:]
                if not current:
                    stop = True
                    continue

                try:
                    idx = signature.mapping.index(current)
                except ValueError:
                    raise _.error('Unknown argument: --%s', current)

                if isinstance(signature.defaults[idx], bool):
                    value = not signature.defaults[idx]
                else:
                    try:
                        value = line.pop(0)
                    except IndexError:
                        raise _.error('Missing argument: --%s', current)

                    if signature.defaults[idx] is not None:
                        _type = type(signature.defaults[idx])
                        try:
                            value = _type(value)
                        except:
                            raise _.error('Invalid argument for %s: "%s"', _type.__name__, value)

                optional[idx] = value
            else:
                if len(positional) < len(signature.positional):
                    positional.append(current)
                else:
                    if casts:
                        name,cast = casts.pop(0)
                        try:
                            if cast == bool:
                                if current.lower() in self.true_values:
                                    current = True
                                elif current.lower() in self.false_values:
                                    current = False
                                else:
                                    raise ValueError
                            value = cast(current)
                        except:
                            raise _.error('Invalid %s for %s: "%s"', cast.__name__, name, current)
                        positional.append(value)
                    else:
                        varargs.append(current)

        if len(positional) < len(signature.positional):
            missing = signature.positional[len(positional):]
            missing += [n for n,c in casts]
            raise _.error('Missing arguments: %s', ' '.join(missing))

        if casts:
            missing = [n for n,c in casts]
            raise _.error('Missing arguments: %s', ' '.join(missing))

        if not signature.varargs and varargs:
            raise _.error('Too many arguments: %s', ' '.join(varargs))

        # let functions know about the size of the terminal
        _terminal_size = os.get_terminal_size()
        self.cols = _terminal_size.columns
        self.rows = _terminal_size.lines

        # concatenate arguments to pass to shell function
        args = positional + optional + varargs
        signature.func(*args)

    def complete(self, text, state):
        def add_args(signature):
            for arg in signature.mapping:
                arg = '--' + arg
                if arg.startswith(text):
                    self.completion_matches.append(arg+' ')

        def find_completer(line, text):
            obj = self
            while True:
                # complete missing command
                if not line:
                    return functools.partial(self.__complete_commands, obj=obj)
                # pop the command name
                command = line.pop(0).lower()
                # get the signature
                signature = obj._signatures.get(command, None)
                if not signature:
                    return None
                # if a signature then return completer
                if isinstance(signature, _Signature):
                    add_args(signature)
                    return getattr(obj, 'complete_' + command, None)
                # drill down to the next level
                obj = signature

        if state == 0:
            # clear matches
            self.completion_matches = []
            # get the original input line
            original = readline.get_line_buffer()
            line = original.split()

            position = len(line)
            # if in the middle of an argument then trim it as it will be in *text*
            if original.endswith(' '):
                position += 1
            else:
                line = line[:-1]

            func = find_completer(line, text)
            if func:
                self.completion_matches += func(line, text, position)

        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def __complete_commands(self, line, text, position, obj=None):
        if obj is None:
            obj = self
        text = text.lower()
        return [n + ' ' for n in obj._signatures if n.startswith(text)]
