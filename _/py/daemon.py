#!/usr/bin/env python

import sys
import os
import atexit
import signal
import time
import inspect
import logging

import _.py


_.py.settings.argparser.add_argument('daemon',
    metavar='(start|stop|restart)',
    help='Control the state of the service')

_.py.settings.argparser.add_argument('--instance',
    help='Name an instance to allow multiple copies to run')

_.py.settings.argparser.add_argument('--foreground', '-F',
    action='store_true',
    help='Stay in the foreground')


class Daemonize(object):
    STDIN  = os.path.devnull
    STDOUT = os.path.devnull
    STDERR = os.path.devnull

    def __init__(self, entry, *args, **kwds):
        self.entry = entry
        self.args  = args
        self.kwds  = kwds

        instance = _.py.args.instance or 'underscore'

        self.pidfile = '/tmp/{}-{}.pid'.format(instance, entry.func_name)

        if 'start' == _.py.args.daemon:
            self.start()
        elif 'stop' == _.py.args.daemon:
            self.stop()
        elif 'restart' == _.py.args.daemon:
            self.restart()
        else:
            raise _.py.error('Unknown daemon option')

    def daemonize(self):
        if _.py.args.foreground:
            logging.debug('Staying in the foreground')
            return

        try:
            pid = os.fork()
        except OSError as e:
            logging.critical('EXCEPTION: os.fork: %d (%s)', e.errno, e.strerror)
            sys.exit(-1)

        if pid > 0:
            sys.exit(0)

        # clear environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # fork again
        try:
            pid = os.fork()
        except OSError as e:
            logging.critical('EXCEPTION: os.fork: %d (%s)', e.errno, e.strerror)
            sys.exit(-1)

        if pid > 0:
            sys.exit(0)

        # redirect file handles
        sys.stdout.flush()
        sys.stderr.flush()

        stdin  = open(self.STDIN,  'r'    )
        stdout = open(self.STDOUT, 'a+'   )
        stderr = open(self.STDERR, 'a+', 0)

        os.dup2(stdin.fileno(),  sys.stdin.fileno() )
        os.dup2(stdout.fileno(), sys.stdout.fileno())
        os.dup2(stderr.fileno(), sys.stderr.fileno())

        # write pidfile
        def atexit_callback():
            try:
                os.remove(self.pidfile)
            except Exception as e:
                logging.warn('Unable to remove PID file: %s', self.pidfile)

        def signal_callback(signum, frame):
            logging.debug('Signal %d received', signum)
            if signum == signal.SIGTERM:
                sys.exit(0)

        atexit.register(atexit_callback)

        signal.signal(signal.SIGTERM, signal_callback)

        with open(self.pidfile, 'wb') as fp:
            fp.write('{}'.format(os.getpid()))

    def _getpid(self):
        pid = None
        if os.path.isfile(self.pidfile):
            try:
                pid = open(self.pidfile, 'r')
                pid = int(pid.read())
            except IOError:
                logging.warn('Unable to open pid file')
                pid = None
            except ValueError:
                logging.warn('Invalid pid value')
                pid = None

            # todo: test if pid is active or stale
        return pid

    def start(self):
        if self._getpid():
            logging.error('Daemon appears to be running')
            sys.exit(-1)

        # Start the daemon
        self.daemonize()

        _.py.settings.components()

        self.entry(*self.args, **self.kwds)

    def stop(self):
        pid = self._getpid()

        if not pid:
            logging.info('Daemon appears to not be running')
            return

        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            if e.errno != 3:
                logging.warn('Error stopping process: %s', e)
                return

        count = 0
        while count < 100:
            try:
                os.kill(pid, 0)
                time.sleep(0.1)
                count += 1
            except OSError as e:
                if e.errno != 3:
                    logging.warn('Error stopping process: %s', e)
                    return
                else:
                    break

        if count == 100:
            logging.warn('Timeout stopping process')
            #return

        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def restart(self):
        self.stop()
        self.start()
