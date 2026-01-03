import dataclasses
from abc import ABCMeta, abstractmethod
from typing import Collection, Mapping


@dataclasses.dataclass(slots=True)
class Rule(metaclass=ABCMeta):
    name: str = dataclasses.field(default=None, kw_only=True)
    description: str = dataclasses.field(default="", kw_only=True)
    tags: Collection[str] = dataclasses.field(default=(), kw_only=True)
    filename: str = dataclasses.field(default=None, kw_only=True)

    def _rule_init(self):
        # NOTE super.__post_init_() doesn't work for some reason.
        if self.name is None:
            self.name = f"{type(self).__name__.casefold()}_{id(self)}"

        if isinstance(self.tags, str):
            self.tags = self.tags.split()

    @abstractmethod
    def run(self, data, context=None) -> "RuleResult":
        ...

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class RuleResult(metaclass=ABCMeta):
    fields = []

    @abstractmethod
    def summary(self) -> Mapping:
        ...
