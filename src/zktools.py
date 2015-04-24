import sys
import logging
from kazoo.client import KazooClient
from argparse import ArgumentParser

class KazooWrapper:
    def __init__(self, hosts):
        self.zk = KazooClient(hosts=hosts)
    def __enter__(self):
        self.zk.start()
        return self
    def __exit__(self, type, value, tb):
        self.zk.stop()
    def __getattr__(self, name):
        return getattr(self.zk, name)
    def __call__( self, *args, **kwds):
        return self.zk._method_call(self.name, self.func, *args, **kwds)

def args(description, **kwargs):
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=30)
    parser = ArgumentParser(description=description) 
    parser.add_argument('path')
    parser.add_argument('--host', default='localhost:2684', help='Zookeeper host to use: [address:port]')
    for k,v in kwargs.iteritems():
        parser.add_argument('--%s' % k, default=v['default'], help=v['help'])
    args = parser.parse_args()
    return args

def stdin():
    return sys.stdin.read().strip()

def kazoo(host):
    zk = KazooWrapper(hosts=host)
    return zk

def rm(zk, path):
    zk.remove(path)
    
def ls(zk, path):
    return zk.get_children(path)
    
def get(zk, path):
    data = zk.get(path)
    return data

def remove(zk, path):
    return zk.delete(path, recursive=True)

def copy(zk, path, dst):
    queue = [path]
    while queue:
        element = queue.pop()
        element_dst = dst + '/' + element
        set(zk, element_dst, get(zk, element)[0])
        logging.info('Copying %s to %s' % (element, element_dst))
        for child in zk.get_children(element):
            queue.append(element + '/' + child)

def set(zk, path, data):
    zk.ensure_path(path)
    zk.set(path, data)

def ok():
    pass

def fail():
    sys.exit(1)
