"""Variable store for managing blueprint variables."""

from dataclasses import dataclass
from typing import Any, Literal, Optional
from PySide6.QtCore import QObject, Signal

from ..utils.consts import variableTypes


VariableType = Literal['string', 'number', 'boolean', 'object', 'array']


@dataclass
class VariableItem:
    """A variable definition."""
    name: str
    type: VariableType
    default_value: Any = None
    current_value: Any = None


class VariableStore(QObject):
    """Store for managing variables."""
    
    # Signals
    variable_changed = Signal()
    
    _instance: Optional['VariableStore'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.variable_map: dict[str, VariableItem] = {}
    
    @classmethod
    def get_instance(cls) -> 'VariableStore':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def create_variable(
        self,
        name: str,
        var_type: VariableType,
        default_value: Any = None
    ) -> bool:
        """Create a new variable.
        
        Returns:
            True if created successfully, False if variable already exists
        """
        if name in self.variable_map:
            print(f'Warning: Variable "{name}" already exists')
            return False
        
        self.variable_map[name] = VariableItem(
            name=name,
            type=var_type,
            default_value=default_value
        )
        self.variable_changed.emit()
        return True
    
    def delete_variable(self, name: str) -> bool:
        """Delete a variable.
        
        Returns:
            True if deleted successfully, False if variable not found
        """
        if name not in self.variable_map:
            return False
        
        del self.variable_map[name]
        self.variable_changed.emit()
        return True
    
    def get_variable(self, name: str) -> Optional[VariableItem]:
        """Get a variable by name."""
        return self.variable_map.get(name)
    
    def get_all_variables(self) -> list[VariableItem]:
        """Get all variables."""
        return list(self.variable_map.values())
    
    def clear_variables(self) -> None:
        """Clear all variables."""
        self.variable_map.clear()
        self.variable_changed.emit()
