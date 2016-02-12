
import inspect
import logging

import _.py

def load(prefix):
    if not _.py.config.has_section('components'):
        return

    components = dict(_.py.config.items('components'))
    for component in components:
        __import__(component)

    #for module, moduleClass in pyaas.module.PyaasModule.registry.items():
    #    moduleClass.load()

    return

ComponentRegistry = {}

class Component(object):
    @staticmethod
    def Decorate(name):
        def _Name(cls):
            ComponentRegistry[name] = cls
            cls._components = {}
            return cls
        return _Name

    @classmethod
    def Loader(cls, name):
        self = cls()

        instances = _.py.config.get('components', name)
        instances = [instance.strip() for instance in instances.split(',')]
        for instance in instances:
            logging.info('Loading %s:%s', name, instance)

            if not _.py.config.has_section(instance):
                logging.warn('No configuration for %s:%s', name, instance)
                continue

            path = cls.__module__ + '.' + instance

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
                module = getattr(module, instance.capitalize())
            except AttributeError:
                raise _.py.error('Component has no class: %s', instance.capitalize())

            params = dict(_.py.config.items(instance))

            self.Load(module, params)

            self._components[instance] = (module,params)
