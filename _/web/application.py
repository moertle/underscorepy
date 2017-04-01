
import sys
import os
import signal
import socket
import logging

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import tornado.web
import tornado.ioloop

import _

from . import handlers

ioloop = tornado.ioloop.IOLoop.instance()


class Application(tornado.web.Application):
    def __init__(self, section='server'):
        signal.signal(signal.SIGINT,  self.SignalHandler)
        signal.signal(signal.SIGTERM, self.SignalHandler)

        self.websockets = set()

        # get the interface and port to listen on
        try:
            self.addr = _.settings.args.address or _.settings.config.get(section, 'address')
        except Exception:
            logging.debug('No address specified')
            self.addr = '127.0.0.1'

        try:
            self.port = _.settings.args.port or _.settings.config.getint(section, 'port')
        except Exception:
            logging.debug('No port specified')
            self.port = 8888

        # load the cookie secret used to encrypt cookies
        cookie_path = _.paths('etc', 'cookie.secret')

        try:
            with open(cookie_path, 'rb') as fp:
                cookie_secret = fp.read(44)
        except IOError:
            cookie_secret = _.web.util.generateCookieSecret(cookie_path)

        # SSL Options
        if not hasattr(self, 'ssl_options'):
            self.ssl_options = None

        # URI patterns
        if not hasattr(self, 'patterns'):
            self.patterns = []

        # Tornado settings
        self.settings = dict(
            static_path   = _.paths('share', 'static'),
            template_path = _.paths('share', 'templates'),
            cookie_secret = cookie_secret,
            debug         = False
        )

        # useful during development
        if _.settings.args.debug:
            self.settings['debug'] = True

            self.patterns.append(
                ( r'/src/(.*)', _.web.handlers.Source ),
                )

        if 'auth' in _.components.Registry:
            for name in _.components.Registry['auth']:
                component = _.components.Registry['auth'][name]
                self.patterns.extend([(component.URL, component)])

            self.patterns.extend([( r'/logout', _.web.auth.Logout )])

            logging.debug('Setting default login URL to: %s', component.URL)
            self.settings['login_url'] = component.URL

    def Listen(self, **kwds):
        # initialize here so patterns and settings can be extended by plugins
        tornado.web.Application.__init__(self, self.patterns, **self.settings)

        if 'ssl_options' not in kwds:
            kwds['ssl_options'] = self.ssl_options

        if 'xheaders' not in kwds:
            kwds['xheaders'] = True

        try:
            self.listen(self.port, self.addr, **kwds)
        except socket.gaierror as e:
            if 8 == e.errno:
                raise _.error('Invalid address specified "%s"' % self.addr)
            raise _.error('Could not listen: %s' % e)
        except socket.error as e:
            raise _.error('Could not listen: %s' % e)
        except Exception as e:
            logging.exception('Exception on listen')
            raise _.error('Could not listen: %s' % e)

        logging.info('Listening on %s:%d', self.addr, self.port)

        ioloop.start()

    def Broadcast(self, msg):
        'Broadcast a message to all connected sockets'

        for client in self.websockets:
            client.write_message(msg)

    def Stop(self):
        ioloop.stop()

    def SignalHandler(self, signum, frame):
        logging.info('Terminating')
        self.Stop()
