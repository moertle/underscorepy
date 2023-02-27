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

import tornado.web

import _

from . import handlers
from . import websockets


class Application(tornado.web.Application):
    def __init__(self, ns=None):
        app = self.__class__.__name__.lower()
        _.settings.load(self, ns=ns, app=app)

        try:
            asyncio.run(self.__async_main())
        except _.error as e:
            logging.error('%s', e)

    async def __async_main(self):
        self.loop   = asyncio.get_event_loop()
        self.__stop = asyncio.Event()

        signal.signal(signal.SIGINT,  self.__signalHandler)
        signal.signal(signal.SIGTERM, self.__signalHandler)

        # Tornado settings
        self.settings = dict(
            static_path   = _.paths('static'),
            template_path = _.paths('templates'),
            debug         = _.args.debug,
            )

        self.patterns   = []
        self.login_urls = []
        self.sessions   = None

        await _.components.load('cache')
        await _.components.load('database')
        await _.components.load('login')

        instance = _.config.get(_.app, 'sessions', fallback=None)
        if instance:
            logging.debug('Sessions cache instance: %s', instance)
            try:
                self.sessions = _.components.cache[instance]
            except KeyError:
                raise _.error('Unknown sessions cache instance: %s', instance)

        await self.initialize()

        if 'cookie_secret' not in self.settings:
            self.settings['cookie_secret'] = await self.cookie_secret()

        for instance,cls in _.components.login.items():
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

        if not self.__stop.is_set():
            await self.__listen()
            await self.__stop.wait()

        for instance in _.components.database.values():
            await instance.close()

        for instance in _.components.cache.values():
            await instance.close()

    async def __listen(self, **kwds):
        # call the Tornado Application init here to give children a chance
        # to initialize patterns and settings
        super(Application, self).__init__(self.patterns, **self.settings)

        if 'xheaders' not in kwds:
            kwds['xheaders'] = True

        try:
            self.listen(_.args.port, _.args.address, **kwds)
        except Exception as e:
            raise _.error(str(e)) from None

        logging.info('Listening on %s:%d', _.args.address, _.args.port)

    async def initialize(self):
        'underscore apps should override this function'

    async def cookie_secret(self):
        'underscore apps should override this function'
        if self.sessions is not None:
            return await self.sessions.cookie_secret()

    async def onLogin(self, handler, user):
        'underscore apps can override this function'

    def periodic(self, timeout, fn, *args, **kwds):
        'run a function or coroutine on a recurring basis'
        async def _periodic():
            while True:
                # bail if the stop event is set
                # otherwise run the function after the timeout occurs
                try:
                    await asyncio.wait_for(self.__stop.wait(), timeout=timeout)
                    break
                except asyncio.TimeoutError as e:
                    pass
                coro = fn(*args, **kwds)
                if asyncio.iscoroutinefunction(coro):
                    await coro
        return asyncio.create_task(_periodic())

    def stop(self):
        logging.debug('Setting stop event')
        self.__stop.set()

    def __signalHandler(self, signum, frame):
        logging.info('Terminating %s', _.app)
        self.loop.call_soon_threadsafe(self.stop)
