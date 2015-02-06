#!/usr/bin/env python3

from app import app

if __name__ == '__main__':
    import os

    host = os.environ.get('SERVER_HOST', 'localhost')
    try:
        port = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        port = 5555
    #app.run(host, port)
    app.run(host='0.0.0.0')

