"""All builtin node definitions."""

from .begin import BeginNodeDefinition
from .log import LogNodeDefinition
from .alert import AlertNodeDefinition
from .if_node import IfNodeDefinition
from .foreach import ForEachNodeDefinition
from .loop import LoopNodeDefinition
from .add import AddNodeDefinition
from .subtract import SubtractNodeDefinition
from .multiply import MultiplyNodeDefinition
from .divide import DivideNodeDefinition
from .equal import EqualNodeDefinition
from .gt import GTNodeDefinition
from .lt import LTNodeDefinition
from .and_node import AndNodeDefinition
from .or_node import OrNodeDefinition
from .not_node import NotNodeDefinition
from .varget import VarGetNodeDefinition
from .varset import VarSetNodeDefinition

# All builtin node definitions
builtinNodeDefinitions = [
    # Core
    BeginNodeDefinition,
    LogNodeDefinition,
    AlertNodeDefinition,
    IfNodeDefinition,
    ForEachNodeDefinition,
    LoopNodeDefinition,
    VarGetNodeDefinition,
    VarSetNodeDefinition,
    
    # Logic
    AddNodeDefinition,
    SubtractNodeDefinition,
    MultiplyNodeDefinition,
    DivideNodeDefinition,
    EqualNodeDefinition,
    GTNodeDefinition,
    LTNodeDefinition,
    AndNodeDefinition,
    OrNodeDefinition,
    NotNodeDefinition,
]


def register_builtin_nodes():
    """Register all builtin node definitions."""
    from ...store.node import NodeStore
    
    node_store = NodeStore.get_instance()
    for definition in builtinNodeDefinitions:
        node_store.reg_node(definition)
