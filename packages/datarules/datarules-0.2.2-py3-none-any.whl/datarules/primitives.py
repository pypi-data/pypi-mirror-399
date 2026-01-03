import inspect
from abc import ABCMeta
from collections.abc import Sequence, Mapping, Callable

import uneval

from .eval_utils import safe_compile, safe_globals
from .expression import collect_expression, rewrite_expression


class Condition(metaclass=ABCMeta):
    @classmethod
    def make(cls, obj, filename=None):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, bool):
            # Always True or always false
            return ExpressionCondition(uneval.to_ast(obj))
        elif not obj:
            # None or empty string means always True
            return ExpressionCondition(uneval.to_ast(True))
        elif isinstance(obj, uneval.ExprType):
            return ExpressionCondition(obj)
        elif callable(obj):
            return FunctionCondition(obj)
        elif isinstance(obj, Sequence) and callable(obj[0]):
            return FunctionCondition(*obj)
        # Should the case below only handle str??
        elif isinstance(obj, Sequence) and isinstance(obj[0], uneval.ExprType):
            return ExpressionCondition(*obj, filename=filename)
        else:
            raise TypeError(f"Unable to handle {obj}")


class ExpressionCondition(Condition):
    def __init__(self, expression: uneval.ExprType, rewrite=True, filename=None):
        expression = uneval.expr(expression)
        node = uneval.to_ast(expression)
        if rewrite:
            node = rewrite_expression(node)
        if filename is None:
            filename = "<condition>"

        collector = collect_expression(node)
        self._expression = uneval.expr(node)
        self._parameters = collector.inputs
        self._compiled = safe_compile(self._expression, filename, 'eval')

    @property
    def expression(self):
        return self._expression

    @property
    def parameters(self):
        return self._parameters

    def __repr__(self):
        return f"{type(self).__name__}({self._expression!r})"

    def __str__(self):
        return str(self._expression)

    def __call__(self, data=None, **kwargs):
        if data is None:
            data = {}

        return eval(self._compiled, safe_globals(kwargs), data)


class FunctionCondition(Condition):
    def __init__(self, function, parameters=None):
        self.function = function

        if parameters is None:
            parameters = inspect.signature(function).parameters
        elif isinstance(parameters, str):
            parameters = parameters.split()

        self.parameters = parameters

    def __repr__(self):
        return f"{type(self)}({self.name}, {self.parameters})"

    def __call__(self, data=None, **kwargs):
        if data is None:
            data = kwargs
        else:
            data = {**data, **kwargs}

        args = (data[param] for param in self.parameters)
        return self.function(*args)

    def __str__(self):
        parameter_str = ", ".join(self.parameters)
        return f"{self.name}({parameter_str})"

    @property
    def name(self):
        return self.function.__name__

    @property
    def description(self):
        return inspect.getdoc(self.function)


class Action(metaclass=ABCMeta):
    @classmethod
    def make(cls, obj, filename=None):
        if isinstance(obj, cls):
            return obj
        elif callable(obj):
            return FunctionAction(obj)
        elif isinstance(obj, str):
            return StringAction(obj, filename=filename)
        elif isinstance(obj, Mapping):
            return ExpressionDictAction(obj, filename=filename)
        else:
            raise TypeError


class StringAction(Action):
    def __init__(self, code: str, filename=None):
        if filename is None:
            filename = '<action>'

        self.code = code
        variables = collect_expression(code)
        self.parameters = variables.inputs
        self.targets = variables.outputs
        self._compiled = safe_compile(code, filename, 'exec')

    def __str__(self):
        return self.code

    def __call__(self, data=None, **kwargs):
        if data is None:
            data = {}
        else:
            data = {parameter: data[parameter] for parameter in self.parameters
                    if parameter in data}

        exec(self._compiled, safe_globals(kwargs), data)
        result = {target: data[target] for target in self.targets}
        return result


class FunctionAction(Action):
    def __init__(self, function, targets=None):
        self.function: Callable[..., Mapping | Sequence] = function

        if isinstance(targets, str):
            targets = targets.split()

        self.parameters: Sequence[str] = inspect.signature(function).parameters
        self.targets: Sequence[str] = targets

    def __str__(self):
        parameter_str = ", ".join(self.parameters)
        return f"{self.name}({parameter_str})"

    def __call__(self, data=None, **kwargs):
        data = {**data, **kwargs}
        data = {k: v for k, v in data.items() if k in self.parameters}
        result = self.function(**data)

        if isinstance(result, Mapping):
            return result
        elif result is not None and self.targets is None:
            raise Exception(f"{self} should return Mapping or targets should be declared.")
        else:
            return dict(zip(self.targets, result, strict=True))

    @property
    def name(self):
        return self.function.__name__

    @property
    def description(self):
        return inspect.getdoc(self.function)


class ExpressionDictAction(Action):
    def __init__(self, actions: Mapping[str, uneval.Expression], filename=None):
        if filename is None:
            filename = '<expression>'
        self.actions = {str(target): uneval.expr(exp) for target, exp in actions.items()}
        self._compiled = {target: safe_compile(exp, filename, 'eval')
                          for target, exp in self.actions.items()}

    @property
    def targets(self):
        return list(self.actions.keys())

    def __str__(self):
        output = []
        for target, action in self.actions.items():
            output.append(f"{target} = {action}")
        return "\n".join(output)

    def __call__(self, df=None, **kwargs):
        gg = safe_globals(kwargs)
        return {target: eval(code, gg, df) for target, code in self._compiled.items()}
