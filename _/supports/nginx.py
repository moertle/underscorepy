#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import logging
import os

import _


class Nginx(_.supports.Support):
    async def init(self, **kwds):
        self.params = dict(
            web_root   = '/var/www/html',
            listen_ip4 = '0.0.0.0',
            listen_ip6 = '[::]',
            conf_path  = '/etc/nginx/sites-available/{server_name}.conf',
            )

        self.params.update(dict(_.config[_.app]))
        self.params.update(kwds)

        _.argparser.add_argument(f'--nginx',
            action='store_true',
            help='install nginx config'
            )

    async def args(self, name):
        if not _.args.nginx:
            return

        logging.info('Installing nginx configuration')

        with open(os.path.join(self.root, 'nginx.conf'), 'r') as fp:
            conf = fp.read()

        try:
            conf = conf.format(**self.params)
        except KeyError as e:
            raise _.error('Missing nginx parameter: %s', e)

        path = self.params['conf_path'].format(**self.params)
        try:
            with open(path, 'w') as fp:
                fp.write(conf)
        except Exception as e:
            raise _.error('Could not write nginx configuration: %s', e)

        _.stop.set()
