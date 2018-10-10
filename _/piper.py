
import logging
import os
import re
import shlex
import subprocess
import tempfile
import time


class Piper(object):
    CMD  = '/bin/sh -c'
    ARGS = ''
    DEFAULTS = {}

    class FileObject(object):
        __slots__ = ['var', 'fullPath', 'fp', 'data']

    def __init__(self, **kwds):
        self.precommand()

        # construct the command line template
        cmd = self.CMD + ' ' + self.ARGS

        stdout = kwds.pop('stdout', os.devnull)
        stdout = open(stdout, 'wb')

        # make a copy of the default arguments
        arguments = self.DEFAULTS.copy()
        # override the defaults from constructor arguments
        for key,value in kwds.items():
            arguments[key] = value
            # make it accessible afterwards as well
            setattr(self, key, value)

        # create containers for FileObjects
        inFiles  = []
        outFiles = []

        # match any parameter that matches {in_*}
        r = re.compile(r'\{in_[\w]+\}')
        idx = 0
        while True:
            match = r.search(cmd[idx:])
            if not match:
                break
            start = idx + 1 + match.start()
            end   = idx - 1 + match.end()
            idx   = idx + match.end()

            fileObject = Piper.FileObject()
            fileObject.var = cmd[start:end]
            fileObject.data = getattr(self, fileObject.var)
            inFiles.append(fileObject)

        # match any parameter that matches {out_*}
        r = re.compile(r'\{out_[\w]+\}')
        idx = 0
        while True:
            match = r.search(cmd[idx:])
            if not match:
                break
            start = idx + 1 + match.start()
            end   = idx - 1 + match.end()
            idx   = idx + match.end()

            fileObject = Piper.FileObject()
            fileObject.var = cmd[start:end]
            outFiles.append(fileObject)

        # make a temp directory for the fifo named pipes
        tmpdir = tempfile.mkdtemp()
        # for each in parameter create the fifo named pipe
        for fileObject in inFiles:
            fileObject.fullPath = os.path.join(tmpdir, fileObject.var)
            fp = open(fileObject.fullPath, 'wb')
            fp.write(self.encode(fileObject.data))
            fp.close()
            arguments[fileObject.var] = fileObject.fullPath

        # for each out parameter create the fifo named pipe
        for fileObject in outFiles:
            fileObject.fullPath = os.path.join(tmpdir, fileObject.var)
            os.mkfifo(fileObject.fullPath)
            arguments[fileObject.var] = fileObject.fullPath

        # apply the dictionary to the command line template
        cmd = cmd.format(**arguments)
        logging.info('%s', cmd)
        cmd = shlex.split(cmd)

        # setup the environment variables
        env = os.environ.copy()

        # call the OpenSSl command with the provided arguments
        process = subprocess.Popen(
            cmd,
            stdout = stdout,
            stderr = stdout,
            env    = env
            )

        # read the data for all the {out_*} parameters
        for fileObject in outFiles:
            fileObject.fp = open(fileObject.fullPath, 'rb')
            fileObject.data = self.decode(fileObject.fp.read())

        # let the process terminate cleanly
        process.wait()

        # remove the temp input files
        for fileObject in inFiles:
            os.remove(fileObject.fullPath)

        # close all the fifo named pipes
        for fileObject in outFiles:
            fileObject.fp.close()
            os.remove(fileObject.fullPath)

        # remove the temp directory
        os.rmdir(tmpdir)

        # set the attributes on the object to the parameter name
        for fileObject in outFiles:
            setattr(self, fileObject.var[4:], fileObject.data)

        self.postcommand()

    def encode(self, data):
        return data.encode('utf-8')

    def decode(self, data):
        return data.decode('utf-8')

    def precommand(self):
        pass

    def postcommand(self):
        pass
