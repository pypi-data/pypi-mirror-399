"""
This won't catch all problems. There are too many potential problems.
Do not run on untrusted input.
"""


import ast
import builtins

from uneval import Expression, to_ast

from .expression import check_expression

# Construct a list of safe builtins
_SAFE_BUILTINS_LIST = ['abs', 'sum', 'all', 'any', 'float', 'hex', 'int', 'bool', 'str',
                       'isinstance', 'len', 'list', 'dict', 'range', 'repr', 'reversed', 'round',
                       'set', 'slice', 'sorted', 'tuple', 'type', 'zip']
SAFE_BUILTINS = {f: getattr(builtins, f) for f in _SAFE_BUILTINS_LIST}


def safe_compile(node, *args, **kwargs):
    """Same as compile but raise error if unsafe."""
    if isinstance(node, str):
        node = ast.parse(node)
    elif isinstance(node, Expression):
        node = to_ast(node)

    safety_analysis = check_expression(node)
    if safety_analysis.problems:
        raise UnsafeCodeError(safety_analysis.problems)

    if not isinstance(node, ast.mod):
        node = ast.Expression(node)

    ast.fix_missing_locations(node)
    return compile(node, *args, **kwargs)


def safe_globals(globals):
    return {'__builtins__': SAFE_BUILTINS, **globals}


class UnsafeCodeError(Exception):
    def __init__(self, problems):
        self.problems = problems

    def __str__(self):
        problem_str = "\n".join(self.problems)
        return f"Code is unsafe:\n{problem_str}"
