
import logging
import types

import _.py


class Component(dict):
    def __init__(self, cls):
        self.cls = cls
        dict.__init__(self)

Registry = {}

def Register(name):
    if name in Registry:
        raise KeyError('There is already a registry for %s' % name)

    def register(cls):
        Registry[name] = Component(cls)
        return cls

    return register

def Load(name):
    try:
        component = Registry[name]
    except KeyError:
        logging.warn('Unable to find component')
        return

    instances = _.py.config.get('components', name)
    instances = [instance.strip() for instance in instances.split(',')]
    for instance in instances:
        logging.info('Loading %s:%s', name, instance)

        if not _.py.config.has_section(instance):
            logging.warn('No configuration for %s:%s', name, instance)
            continue

        path = component.cls.__module__ + '.' + instance
        try:
            module = __import__(path)
        except ImportError:
            path = instance
            try:
                module = __import__(path)
            except ImportError:
                raise _.py.error('Component not found: %s', instance)

        for p in path.split('.')[1:]:
            module = getattr(module, p)

        try:
            className = instance.rsplit('.', 1)[-1]
            className = className.capitalize()
            module = getattr(module, className)
        except AttributeError:
            raise _.py.error('Component %s has no class: %s', instance, className)

        config = dict(_.py.config.items(instance))

        if hasattr(module, '_pyConfig'):
            module._pyConfig(config)

        component[instance] = module

        if hasattr(component.cls, '_pyLoad'):
            component.cls._pyLoad(component)
