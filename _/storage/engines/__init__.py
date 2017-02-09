
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
        instances = config.pop('instances', name)

        for instance in [i.strip() for i in instances.split(',')]:
            instance_config = dict(config)
            if instance != name:
                instance_config.update(_.settings.config.items(instance))

            critical = instance_config.pop('critical', '')
            if critical.lower() in ['t', 'y', 'true', 'yes', '1']:
                critical = True
            else:
                critical = False

            try:
                engine = engineCls(**instance_config)
            except Exception as e:
                logging.error('Unable to connect to database: %s', instance)
                logging.debug('%s', e)
                if critical:
                    raise _.error('Database marked as critical')
                continue

            _.storage.databases[instance] = engine
