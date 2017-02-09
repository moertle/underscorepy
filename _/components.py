
import logging
import types

import _


Registry = {}

def Register(name):
    class Component(dict):
        def __init__(self, cls):
            self.cls = cls
            dict.__init__(self)

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

    instances = _.settings.config.get('components', name)
    instances = [instance.strip() for instance in instances.split(',')]
    for instance in instances:
        logging.info('Loading %s:%s', name, instance)

        if not _.settings.config.has_section(instance):
            logging.warn('No configuration for %s:%s', name, instance)
            continue

        config = dict(_.settings.config.items(instance))

        path = component.cls.__module__ + '.' + instance
        try:
            module = __import__(path)
        except ImportError:
            path = instance
            try:
                module = __import__(path)
            except ImportError:
                raise _.error('Component not found: %s', instance)

        for subpath in path.split('.')[1:]:
            module = getattr(module, subpath)

        try:
            className = instance.rsplit('.', 1)[-1]
            className = className.capitalize()
            module = getattr(module, className)
        except AttributeError:
            raise _.error('Component %s has no class: %s', instance, className)

        if hasattr(module, '_pyConfig'):
            module._pyConfig(config)

        component[instance] = module

        if hasattr(component.cls, '_pyLoad'):
            component.cls._pyLoad(instance, module, config)
