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


class Application(tornado.web.Application):
    @classmethod
    def main(cls, ns=None):
        self = cls()
        try:
            asyncio.run(self.__async_main(ns))
        except _.error as e:
            if _.args.debug:
                traceback.print_tb(e.__traceback__)
            logging.error('%s', e)

    async def __async_main(self, ns):
        self.loop = asyncio.get_event_loop()

        signal.signal(signal.SIGINT,  self.__signalHandler)
        signal.signal(signal.SIGTERM, self.__signalHandler)

        app = self.__class__.__name__.lower()
        try:
            await _.settings.load(self, ns=ns, app=app)
            await self.logging()
        except _.error as e:
            if _.args.debug:
                traceback.print_tb(e.__traceback__)
            logging.error('%s', e)
            self.stop()

        if not _.stop.is_set():
            for name,component in _.login.items():
                try:
                    await _.wait(component.args(name))
                except _.error as e:
                    logging.error('%s', e)
                    self.stop()
                    break

        if not _.stop.is_set():
            for name,component in _.support.items():
                try:
                    await _.wait(component.args(name))
                except _.error as e:
                    logging.error('%s', e)
                    self.stop()
                    break

        if not _.stop.is_set():
            try:
                await self.__async_init()
            except _.error as e:
                logging.error('%s', e)

        for name,component in _.database.items():
            await component.close()

        for name,component in _.cache.items():
            await component.close()

    async def __async_init(self, **kwds):
        self.patterns   = []
        self.login_urls = []

        # check if a sessions cache was specified
        _.sessions = _.config.get(_.app, 'sessions', fallback=None)
        if _.sessions:
            logging.debug('Sessions cache: %s', _.sessions)
            try:
                _.sessions = _.cache[_.sessions]
            except KeyError:
                raise _.error('Unknown sessions cache instance: %s', _.sessions)

        # call the child applications entry point
        try:
            await _.wait(self.initialize())
        except NotImplementedError:
            logging.warning('No "initialize" function defined')

        if 'cookie_secret' not in self.settings:
            self.settings['cookie_secret'] = await self.cookie_secret()

        for instance,cls in _.login.items():
            self.login_urls.append((f'/login/{instance}', cls))

        if self.login_urls:
            self.patterns = self.login_urls + self.patterns
            self.patterns = [
                ( r'/login',  _.handlers.LoginPage ),
                ( r'/logout', _.handlers.Logout    ),
                ] + self.patterns
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

        # add the handlers to the logger
        if _.config.getboolean(_.app, 'logging', fallback=False):
            full_path = _.paths(f'{_.app}.log')
            file_logger = logging.FileHandler(full_path)
            file_logger.setLevel(logging.DEBUG if _.args.debug else logging.INFO)
            file_logger.setFormatter(
                logging.Formatter(
                    fmt = '%(asctime)s %(levelname)-8s %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    )
                )
            root_logger = logging.getLogger()
            root_logger.addHandler(file_logger)

    async def cookie_secret(self):
        'underscore apps can override this function'
        if _.sessions is not None:
            return await _.wait(_.sessions.cookie_secret())

    async def on_login(self, handler, user, *args, **kwds):
        'underscore apps should override this function'
        raise NotImplementedError

    def periodic(self, _timeout, fn, *args, **kwds):
        'run a function or coroutine on a recurring basis'
        async def _periodic():
            while True:
                # bail if the stop event is set
                # otherwise run the function after the timeout occurs
                try:
                    await asyncio.wait_for(_.stop.wait(), timeout=_timeout)
                    break
                except asyncio.TimeoutError as e:
                    pass
                try:
                    result = await _.wait(fn(*args, **kwds))
                except Exception as e:
                    logging.exception(e)
        return asyncio.create_task(_periodic())

    def stop(self):
        logging.debug('Setting stop event')
        _.stop.set()

    def __signalHandler(self, signum, frame):
        'handle signals in a thread-safe way'
        signame = signal.Signals(signum).name
        handler = getattr(self, f'on_{signame.lower()}', None)
        if handler:
            stop = handler(signum, frame)
            if stop:
                return
        logging.info('Terminating %s on %s signal', _.app, signame)
        self.loop.call_soon_threadsafe(self.stop)

    # demonstrate a specific signal handler
    # and print newline after ^C on terminals
    def on_sigint(self, signum, frame):
        print()
