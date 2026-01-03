from collections import defaultdict
from collections.abc import Sequence
from graphlib import TopologicalSorter

from datarules import Correction, CorrectionList


def toposort(corrections: Sequence[Correction], inplace: bool = False):
    """This sorts corrections, such that dependent variables are corrected first.

    For this to work:
    - Each correction should (correctly) declare its targets.
    - Corrections may not have cycles.

    inplace - Replace corrections instead of returning a new list.
    """

    name_to_correction = {corr.name: corr for corr in corrections}
    target_to_corrections = _make_target_to_corrections(corrections)

    ts = TopologicalSorter()
    for corr in corrections:
        dependencies = set(corr.trigger.parameters) | set(corr.action.parameters)
        dependency_names = [name for dep in dependencies
                            for name in target_to_corrections[dep]]
        ts.add(corr.name, *dependency_names)

    new_corrections = CorrectionList(name_to_correction[name] for name in ts.static_order())
    if inplace:
        corrections[:] = new_corrections
    else:
        return new_corrections


def _make_target_to_corrections(corrections):
    target_to_corrections = defaultdict(list)
    for corr in corrections:
        targets = getattr(corr.action, 'targets', None)
        if targets is not None:
            for target in targets:
                target_to_corrections[target].append(corr.name)
        else:
            raise Exception(f"Please specify targets on {corr}.")
    return target_to_corrections
