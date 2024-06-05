<<<<<<< HEAD
import logging
from functools import partial
from typing import Tuple, Mapping, List

from genno.operator import broadcast_map
from ixmp.report import Key
from .pyam import collapse_message_cols

# Assuming TASKS1 was where Sankey tasks were defined:
TASKS1 = (
    ("message::sankey", "concat", "out::pyam", "in::pyam"),
)

def get_sankey_tasks() -> List[Tuple[Tuple, Mapping]]:
    """Return a list of tasks for Sankey diagram reporting."""
    to_add: List[Tuple[Tuple, Mapping]] = []
    strict = dict(strict=True)

    # This might include specific Sankey diagram configuration or additional tasks.
    for t in TASKS1:
        to_add.append((t, strict))

    return to_add

class SankeyReporter:
    """A specialized reporter for generating Sankey diagrams."""

    @staticmethod
    def add_tasks(reporter, fail_action: str = "raise") -> None:
        """Add Sankey-related tasks to a given reporter."""
        reporter.add_queue(get_sankey_tasks(), fail=fail_action)

# This class can then be imported and used in your main reporting script to add Sankey tasks.
=======
import logging
from functools import partial
from typing import Tuple, Mapping, List

from genno.operator import broadcast_map
from ixmp.report import Key
from .pyam import collapse_message_cols

# Assuming TASKS1 was where Sankey tasks were defined:
TASKS1 = (
    ("message::sankey", "concat", "out::pyam", "in::pyam"),
)

def get_sankey_tasks() -> List[Tuple[Tuple, Mapping]]:
    """Return a list of tasks for Sankey diagram reporting."""
    to_add: List[Tuple[Tuple, Mapping]] = []
    strict = dict(strict=True)

    # This might include specific Sankey diagram configuration or additional tasks.
    for t in TASKS1:
        to_add.append((t, strict))

    return to_add

class SankeyReporter:
    """A specialized reporter for generating Sankey diagrams."""

    @staticmethod
    def add_tasks(reporter, fail_action: str = "raise") -> None:
        """Add Sankey-related tasks to a given reporter."""
        reporter.add_queue(get_sankey_tasks(), fail=fail_action)

# This class can then be imported and used in your main reporting script to add Sankey tasks.
>>>>>>> 72ca946039b356740f500ef0fd141d03bea6ed50
