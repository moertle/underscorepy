
import sys
import os
import io
import zipfile

import _

def package(main, includes):
    zio = io.BytesIO()
    zf = zipfile.ZipFile(zio, 'w', zipfile.ZIP_DEFLATED)

    zf.write(main, '__main__.py')

    for include in includes:
        root = os.path.abspath(include)
        trim = os.path.dirname(root)
        for base,directories,filenames in os.walk(root):
            for filename in filenames:
                path = os.path.join(base, filename)
                arcname = path[len(trim)+1:]
                zf.write(path, arcname)
    zf.close()

    bits = zio.getvalue()
    return bits


if '__main__' == __name__:
    output   = sys.argv[1]
    main     = sys.argv[2]
    includes = sys.argv[3:]

    zipdata = package(main, includes)

    fp = open(output, 'wb')
    fp.write(b'#!/usr/bin/env python3\n')
    fp.write(zipdata)
    fp.close()

    os.chmod(output, 0o755)
