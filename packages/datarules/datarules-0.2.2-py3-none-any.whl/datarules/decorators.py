import inspect

from .check import Check
from .correction import Correction
from .primitives import FunctionAction


def check(f=None, /, *, name=None, description=None, tags=()):
    def accept(g):
        return Check(name=name or g.__name__,
                     description=description or inspect.getdoc(g),
                     test=g,
                     tags=tags,
                     )

    if f is None:
        return accept
    else:
        return accept(f)
    
    
def correction(f=None, /, *, trigger=None, targets=None, name=None, description=None, tags=()):
    def accept(g):
        return Correction(name=name or g.__name__,
                          description=description or inspect.getdoc(g),
                          trigger=trigger,
                          action=FunctionAction(g, targets=targets),
                          tags=tags,
                          )

    if f is None:
        return accept
    else:
        return accept(f)
