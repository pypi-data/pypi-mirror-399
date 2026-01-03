import os
from abc import ABCMeta
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import MutableSequence, Mapping, Iterable

from . import Check, Correction
from .report import CheckReport, CorrectionReport, Report
from .rule import Rule


class RuleList(MutableSequence, metaclass=ABCMeta):
    element_type = Rule
    report_type = Report

    @classmethod
    def from_file(cls, path: os.PathLike | str):
        suffix = Path(path).suffix
        if suffix == ".py":
            return cls._from_pyfile(path)
        else:
            with open(path) as fp:
                match suffix:
                    case ".yaml":
                        import yaml
                        data = yaml.safe_load(fp)
                    case ".json":
                        import json
                        data = json.load(fp)
                    case _:
                        raise ValueError(f"Unknown suffix: {suffix}")
                return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Mapping | Iterable[Mapping]):
        if isinstance(data, Mapping) and "rules" in data:
            data = data["rules"]
        return cls(cls.element_type.from_dict(r) for r in data)

    @classmethod
    def _from_pyfile(cls, path: os.PathLike):
        filename = str(path)
        loader = SourceFileLoader("rules", filename)
        module = ModuleType(loader.name)
        loader.exec_module(module)
        rules = cls(filename=filename)
        for name, value in module.__dict__.items():
            if isinstance(value, cls.element_type):
                value.name = name
                rules.append(value)
        return rules

    def __init__(self, rules=(), filename='<unknown>'):
        self._rules = []
        self.extend(rules)
        self.filename = filename

    def __iter__(self):
        return iter(self._rules)

    def __len__(self):
        return len(self._rules)

    def __getitem__(self, index):
        return self._rules[index]

    def __setitem__(self, index, rule: Rule | Iterable[Rule]):
        if isinstance(index, int) and not isinstance(rule, self.element_type):
            raise TypeError(f"{rule} is not {self.element_type.__name__}")
        if isinstance(index, slice) and not all(isinstance(r, self.element_type) for r in rule):
            raise TypeError(f"{rule} is not Iterable[{self.element_type.__name__}]")

        self._rules[index] = rule

    def __delitem__(self, index: int) -> None:
        del self._rules[index]

    def insert(self, index, rule):
        if not isinstance(rule, self.element_type):
            raise TypeError(f"{rule} is not {self.element_type.__name__}")
        self._rules.insert(index, rule)

    def run(self, df, context=None):
        results = [rule.run(df, context) for rule in self]
        return self.report_type(results)


class CheckList(RuleList):
    element_type = Check
    report_type = CheckReport


class CorrectionList(RuleList):
    element_type = Correction
    report_type = CorrectionReport
