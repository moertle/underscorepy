#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import asyncio
import logging
import os
import signal
import socket
import sys
import traceback

import tornado.web

import _

from . import handlers
from . import websockets


class Application(tornado.web.Application):
    __entry_points = []

    @classmethod
    def Entry(cls, fn):
        Application.__entry_points.append(fn)
        return fn

    def __init__(self, ns=None):
        try:
            asyncio.run(self.__async_main(ns))
        except _.error as e:
            logging.error('%s', e)
            if _.args.debug:
                traceback.print_tb(e.__traceback__)

    async def __async_main(self, ns):
        self.loop   = asyncio.get_event_loop()

        signal.signal(signal.SIGINT,  self.__signalHandler)
        signal.signal(signal.SIGTERM, self.__signalHandler)

        app = self.__class__.__name__.lower()
        try:
            await _.settings.load(self, ns=ns, app=app)
            await self.logging()
        except _.error as e:
            self.stop()

        if not _.stop.is_set():
            for name,component in _.login.items():
                try:
                    await component.args(name)
                except _.error as e:
                    logging.error('%s', e)
                    self.stop()

        if not _.stop.is_set():
            await self.__async_init()

        for name,component in _.database.items():
            await component.close()

        for name,component in _.cache.items():
            await component.close()

    async def __async_init(self, **kwds):
        self.patterns   = []
        self.login_urls = []

        # Tornado settings
        self.settings = dict(
            static_path   = _.paths('static'),
            template_path = _.paths('templates'),
            debug         = _.args.debug,
            )

        # check if a sessions cache was specified
        self.sessions = _.config.get(_.app, 'sessions', fallback=None)
        if self.sessions:
            logging.debug('Sessions cache: %s', self.sessions)
            try:
                self.sessions = _.cache[self.sessions]
            except KeyError:
                raise _.error('Unknown sessions cache instance: %s', self.sessions)

        # call the child applications entry point
        if Application.__entry_points:
            for fn in Application.__entry_points:
                await _.wait(fn(self))
        else:
            try:
                await _.wait(self.initialize())
            except NotImplementedError:
                logging.warning('No entry point defined')

        if 'cookie_secret' not in self.settings:
            self.settings['cookie_secret'] = await self.cookie_secret()

        for instance,cls in _.login.items():
            self.login_urls.append((f'/login/{instance}', cls))

        if self.login_urls:
            self.patterns.extend(self.login_urls)
            self.patterns.extend([
                ( r'/login',  _.handlers.LoginPage ),
                ( r'/logout', _.handlers.Logout    ),
                ])
            self.settings['login_url'] = '/login'

        self.patterns.append(
            ( r'/(favicon.ico)', tornado.web.StaticFileHandler, {'path':''}),
            )

        await self.__listen()
        await _.stop.wait()

    async def __listen(self, **kwds):
        # call the Tornado Application init here to give children a chance
        # to initialize patterns and settings
        super(Application, self).__init__(self.patterns, **self.settings)

        if 'xheaders' not in kwds:
            kwds['xheaders'] = True

        try:
            self.listen(_.args.port, _.args.address, **kwds)
        except Exception as e:
            raise _.error('%s', e) from None

        logging.info('Listening on %s:%d', _.args.address, _.args.port)

    async def initialize(self):
        'underscore apps should override this function'
        raise NotImplementedError

    async def logging(self):
        'underscore apps can override or extend this function'

        logging.basicConfig(
            format  = '%(asctime)s %(levelname)-8s %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S',
            level   = logging.DEBUG if _.args.debug else logging.INFO,
            force   = True
            )

        # add the handlers to the logger
        if _.config.getboolean(_.app, 'logging', fallback=False):
            fullPath = _.paths(f'{_.app}.log')
            fileLogger = logging.FileHandler(fullPath)
            fileLogger.setLevel(logging.DEBUG if _.args.debug else logging.INFO)
            fileLogger.setFormatter(
                logging.Formatter(
                    fmt = '%(asctime)s %(levelname)-8s %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    )
                )
            rootLogger = logging.getLogger()
            rootLogger.addHandler(fileLogger)

    async def cookie_secret(self):
        'underscore apps can override this function'
        if self.sessions is not None:
            return await self.sessions.cookie_secret()

    async def on_login(self, handler, user, *args, **kwds):
        'underscore apps can override this function'

    def periodic(self, timeout, fn, *args, **kwds):
        'run a function or coroutine on a recurring basis'
        async def _periodic():
            while True:
                # bail if the stop event is set
                # otherwise run the function after the timeout occurs
                try:
                    await asyncio.wait_for(_.stop.wait(), timeout=timeout)
                    break
                except asyncio.TimeoutError as e:
                    pass
                await _.wait(fn(*args, **kwds))
        return asyncio.create_task(_periodic())

    def stop(self):
        logging.debug('Setting stop event')
        _.stop.set()

    def __signalHandler(self, signum, frame):
        logging.info('Terminating %s', _.app)
        self.loop.call_soon_threadsafe(self.stop)
