
import os
import base64

def generateCookieSecret(path):
    secret = base64.b64encode(os.urandom(32))
    with open(path, 'wb') as fp:
        fp.write(secret)
    return secret
