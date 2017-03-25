
# classes are dynamically imported if storage is enabled

import logging

import _


@_.components.Register('storage')
class Storage(object):
    @classmethod
    def _pyConfig(cls, *args, **kwds):
        pass

    @classmethod
    def _pyLoad(cls, name, engineCls, config):
        # support multiple instances or fallback to the name of the driver
        instances = config.pop('instances', name)

        for instance in [i.strip() for i in instances.split(',')]:
            instance_config = dict(config)
            if instance != name:
                instance_config.update(_.settings.config.items(instance))

            critical = instance_config.pop('critical', 'true')
            if critical.lower() in ['f', 'false', 'n', 'no', '0']:
                critical = False
            else:
                critical = True

            try:
                _.storage.instances[instance] = engineCls(**instance_config)
            except Exception as e:
                if critical:
                    raise _.error('Unable to connect to %s: %s', instance, e)
                else:
                    logging.error('Unable to connect to %s: %s', instance, e)
                continue

    def Initialize(self):
        return
