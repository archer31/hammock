import requests

class Hammock(object):

    HTTP_METHODS = ['get', 'options', 'head', 'post', 'put', 'patch', 'delete']

    def __init__(self, name=None, parent=None):
        """Constructor

        Arguments:
            name -- name of node. If this node is root, used as client base_url
            parent -- parent node for chaining
            client_ops -- `wrest` client constructor options
        """
        self._name = name
        self._parent = parent

    def __getattr__(self, name):
        """ Here comes some magic. Any absent attribute typed within class falls
        here and return a new child `Hammock` instance in the chain.
        """
        return Hammock(name=name, parent=self)

    def __iter__(self):
        """ Iterator implementation which iterates over `Hammock` chain."""
        current = self
        while current:
            if current._name:
                yield current
            current = current._parent

    def _chain(self, *args):
        """ This method converts args into chained Hammock instances

        Arguments:
            args -- array of string representable objects
        """
        chain = self
        for arg in args:
            chain = Hammock(name=str(arg), parent=chain)
        return chain

    def __call__(self, *args):
        """ Here comes second magic. If any `Hammock` instance called it returns
        a new child `Hammock` instance in the chain
        """
        return self._chain(*args)

# Bind `requests` module HTTP verb methods
def bind_method(method):
    def f(hammock, *args, **kwargs):
        path_comps = [mock._name for mock in hammock._chain(*args)] 
        url = "/".join(reversed(path_comps))
        return requests.request(method, url, **kwargs)
    return f

for method in Hammock.HTTP_METHODS:
    setattr(Hammock, method.upper(), bind_method(method))