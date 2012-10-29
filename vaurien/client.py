from contextlib import contextmanager
from urlparse import urlparse
import requests


class Client(object):
    def __init__(self, host='localhost', port=8080, scheme='http'):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.root_url = '%s://%s:%s' % (scheme, host, port)
        self.handler_url = self.root_url + '/handler'
        self.list_handlers_url = self.root_url + '/handlers'

    def set_handler(self, handler):
        res = requests.post(self.handler_url, data=handler)
        if res.status_code != 200 or res.content != 'ok':
            raise ValueError(res.content)

    def get_handler(self):
        res = requests.get(self.handler_url)
        if res.status_code != 200:
            raise ValueError(res.content)
        return res.content

    def list_handlers(self):
        res = requests.get(self.list_handlers_url)
        if res.status_code != 200:
            raise ValueError(res.content)
        return res.json['handlers']

    @contextmanager
    def with_handler(self, handler):
        current = self.get_handler()
        self.set_handler(handler)
        try:
            yield
        finally:
            self.set_handler(current)


def main():
    """Command-line tool to change the handler that's being used by vaurien"""
    import argparse
    parser = argparse.ArgumentParser(description='Change the vaurien handler')
    parser.add_argument('action', help='The action you want to do.',
                    choices=['list-handlers', 'set-handler', 'get-handler'])
    parser.add_argument('handler', nargs='?',
                    help='The vaurien handler to set for the next calls')
    parser.add_argument('--host', dest='host', default='http://localhost:8080',
                    help='The host to use. Provide the scheme.')

    args = parser.parse_args()
    parts = urlparse(args.host)
    scheme = parts.scheme
    host, port = parts.netloc.split(':', -1)
    client = Client(host, port, scheme)
    if args.action == 'list-handlers':
        print client.list_handlers()
    elif args.action == 'set-handler':
        try:
            client.set_handler(args.handler)
            print 'Handler changed to "%s"' % args.handler
        except ValueError:
            print 'The request failed. Please use one of %s' %\
                ', '.join(client.list_handlers())
    elif args.action == 'get-handler':
        print client.get_handler()
