"""
AINative CLI Module

Modular CLI structure with separate command groups.
"""

from .agents import agents_group
from .swarm import swarm_group
from .tasks import task_group
from .coordination import coordination_group
from .learning import learning_group
from .state import state_group
from .local import local_group
from .inspect import inspect_group
from .sync import sync_group


__all__ = [
    "agents_group",
    "swarm_group",
    "task_group",
    "coordination_group",
    "learning_group",
    "state_group",
    "local_group",
    "inspect_group",
    "sync_group",
]
