
import logging
import os
import re
import subprocess
import tempfile
import time


class Piper(object):
    CMD  = '/bin/sh'
    ARGS = ''
    DEFAULTS = {}

    class FileObject(object):
        __slots__ = ['var', 'fullPath', 'fp', 'data']

    def __init__(self, **kwds):
        # construct the command line template
        cmd = self.CMD + ' ' + self.ARGS

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
            os.mkfifo(fileObject.fullPath)
            arguments[fileObject.var] = fileObject.fullPath

        # for each out parameter create the fifo named pipe
        for fileObject in outFiles:
            fileObject.fullPath = os.path.join(tmpdir, fileObject.var)
            os.mkfifo(fileObject.fullPath)
            arguments[fileObject.var] = fileObject.fullPath

        # apply the dictionary to the command line template
        cmd = cmd.format(**arguments)
        logging.info('%s', cmd)
        cmd = cmd.split(None)

        # setup the environment variables
        env = os.environ.copy()

        # call the OpenSSl command with the provided arguments
        process = subprocess.Popen(
            cmd,
            stdout = open(os.devnull, 'w'),
            stderr = open(os.devnull, 'w'),
            env    = env
            )

        # write the data for all the {in_*} parameters
        for fileObject in inFiles:
            fileObject.fp = open(fileObject.fullPath, 'wb')
            fileObject.fp.write(fileObject.data)

        # read the data for all the {out_*} parameters
        for fileObject in outFiles:
            fileObject.fp = open(fileObject.fullPath, 'rb')
            fileObject.data = fileObject.fp.read()

        # let the process terminate cleanly
        process.wait()

        # close all the fifo named pipes
        for fileObject in inFiles:
            fileObject.fp.close()
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



#
#class DHParams(Piper):
#    ARGS = 'dhparam -out {out_dh} {keysize}'
#    DEFAULTS = {
#        'keysize' : Piper.KEY_SIZE,
#    }
#
#
#class InitCA(Piper):
#    ARGS = 'req -batch -days {days} -nodes -new -newkey rsa:{keysize} -x509 -keyout {out_key} -out {out_crt}'
#    DEFAULTS = {
#        'keysize' : Piper.KEY_SIZE,
#        'days'    : 3650,
#    }
#
#
#dhparams = DHParams()
#initca = InitCA(keysize=2048)
#
#print
#print dhparams.dh
#print
#print initca.keysize
#print initca.key
#print initca.crt
#print
#
