"""Code compiler for generating HOI4 MOD scripts from blueprint."""

from typing import Optional
from ..store.node import NodeStore, CodeckNode, CodeckNodeDefinition, CodeImportPrepare, CodeFunctionPrepare
from ..store.connection import ConnectionStore, ConnectInfo
from ..store.variable import VariableStore
from ..store.settings import tr
from ..utils.consts import STANDARD_PIN_EXEC_OUT
from ..utils.string_helper import format_function_indent


class CodeCompiler:
    """Compiler that generates HOI4 MOD script code from blueprint nodes."""
    
    def __init__(self):
        self.prepares: list = []
        self._prepare_ids: set = set()  # For efficient duplicate checking
        self.script_type = 'event'  # 'event', 'decision', 'national_focus', 'idea'
        self.mod_namespace = 'my_mod'
        self.print_comment = True
    
    @property
    def node_map(self):
        return NodeStore.get_instance().node_map
    
    @property
    def node_definition(self):
        return NodeStore.get_instance().node_definition
    
    @property
    def connections(self):
        return ConnectionStore.get_instance().connections
    
    @property
    def variable_map(self):
        return VariableStore.get_instance().variable_map
    
    def generate(self) -> str:
        """Generate code from the blueprint."""
        begin = self._find_begin()
        code_text = ''
        
        code_text += self._generate_variable()
        code_text += self._generate_code_from_node(self._get_exec_next(begin.id))
        
        # Add prepare code at the beginning
        code_text = self._generate_prepare_code() + code_text
        
        return code_text
    
    def _generate_code_from_node(self, start_node: Optional[CodeckNode]) -> str:
        """Generate code starting from a node."""
        code_text = ''
        current_node = start_node
        
        while current_node is not None:
            definition = self.node_definition.get(current_node.name)
            if not definition:
                current_node = self._get_exec_next(current_node.id)
                continue
            
            self._collect_prepare(definition)
            
            code_fn = definition.code_fn
            node = current_node
            
            if code_fn:
                def build_pin_var_name(pin_name: str, node_id: Optional[str] = None) -> str:
                    return self._build_pin_var_name(pin_name, node_id or node.id)
                
                if self.print_comment:
                    code_text += f'# {node.id} (node: {definition.name})\n'
                
                code_text += code_fn(
                    node=node,
                    build_pin_var_name=build_pin_var_name,
                    get_connection_input=lambda pin_name, node_id=None: self._get_connection_input(pin_name, node_id or node.id),
                    get_connection_exec_output=lambda pin_name, node_id=None: self._get_connection_exec_output(pin_name, node_id or node.id)
                )
            
            current_node = self._get_exec_next(current_node.id)
        
        return code_text
    
    def _build_pin_var_name(self, pin_name: str, node_id: str) -> str:
        """Build a variable name for a pin."""
        return f'_{node_id}_{pin_name}'
    
    def _get_connection_input(self, pin_name: str, node_id: str) -> Optional[str]:
        """Get the input connection code for a pin."""
        connection = None
        for conn in self.connections:
            if conn.to_node_id == node_id and conn.to_node_pin_name == pin_name:
                connection = conn
                break
        
        if not connection:
            return None
        
        from_node = self.node_map.get(connection.from_node_id)
        if not from_node:
            return None
        
        # Special handling for varget node
        if from_node.name == 'varget':
            return from_node.data.get('name', '')
        
        from_node_def = self.node_definition.get(from_node.name)
        if not from_node_def:
            return None
        
        # Find output pin definition
        output_def = None
        for out in from_node_def.outputs:
            if out.name == connection.from_node_pin_name:
                output_def = out
                break
        
        if not output_def:
            return None
        
        # Check for custom output code function
        output_code_fn = from_node_def.output_code_fns.get(connection.from_node_pin_name)
        if output_code_fn:
            self._collect_prepare(from_node_def)
            
            def build_pin_var_name(pin_name: str, node_id: Optional[str] = None) -> str:
                return self._build_pin_var_name(pin_name, node_id or from_node.id)
            
            return output_code_fn(
                node=from_node,
                build_pin_var_name=build_pin_var_name,
                get_connection_input=lambda pin_name, node_id=None: self._get_connection_input(pin_name, node_id or from_node.id),
                get_connection_exec_output=lambda pin_name, node_id=None: self._get_connection_exec_output(pin_name, node_id or from_node.id)
            ) or ''
        else:
            # Direct value reference
            return self._build_pin_var_name(
                connection.from_node_pin_name,
                connection.from_node_id
            )
    
    def _get_connection_exec_output(self, pin_name: str, node_id: str) -> Optional[str]:
        """Get the execution output code for a pin."""
        exec_node = self._get_exec_next(node_id, pin_name)
        if not exec_node:
            return None
        
        return self._generate_code_from_node(exec_node)
    
    def _generate_variable(self) -> str:
        """Generate variable declarations in HOI4 script format."""
        variables = list(self.variable_map.values())
        if not variables:
            return ''
        
        lines = []
        lines.append('# 变量定义 / Variable Definitions')
        for var in variables:
            if var.default_value is None:
                lines.append(f'# {var.name} = undefined')
            else:
                # HOI4 uses set_variable for variable assignment
                if var.type == 'number':
                    lines.append(f'set_variable = {{ var = {var.name} value = {var.default_value} }}')
                else:
                    lines.append(f'# {var.name} = {var.default_value}')
        
        return '\n'.join(lines) + '\n\n'
    
    def _generate_prepare_code(self) -> str:
        """Generate prepare code header for HOI4 MOD scripts."""
        prepare_code = ''
        
        # Add HOI4 script header
        prepare_code += f'# HOI4 MOD Script\n'
        prepare_code += f'# Generated by Codeck Visual Blueprint Editor\n'
        prepare_code += f'# Namespace: {self.mod_namespace}\n'
        prepare_code += f'# Type: {self.script_type}\n'
        prepare_code += '\n'
        
        # Add script type wrapper
        if self.script_type == 'event':
            prepare_code += f'add_namespace = {self.mod_namespace}\n\n'
        
        return prepare_code
    
    def _find_begin(self) -> CodeckNode:
        """Find the Begin node.
        
        Returns:
            The Begin node
            
        Raises:
            ValueError: If no Begin node found or multiple Begin nodes found
        """
        begin_nodes = [
            node for node in self.node_map.values()
            if self.node_definition.get(node.name, None) and 
               self.node_definition[node.name].type == 'begin'
        ]
        
        if not begin_nodes:
            raise ValueError(tr('no_begin_node'))
        
        if len(begin_nodes) > 1:
            raise ValueError(tr('multiple_begin_nodes'))
        
        return begin_nodes[0]
    
    def _get_exec_next(self, node_id: str, pin_name: str = STANDARD_PIN_EXEC_OUT) -> Optional[CodeckNode]:
        """Get the next node connected to an exec pin.
        
        Args:
            node_id: The source node ID
            pin_name: The exec pin name (default: standard exec out)
            
        Returns:
            The next node or None if not connected
            
        Raises:
            ValueError: If multiple connections found from the same exec pin
        """
        node = self.node_map.get(node_id)
        if not node:
            return None
        
        exec_connections = [
            conn for conn in self.connections
            if conn.from_node_id == node_id and conn.from_node_pin_name == pin_name
        ]
        
        if not exec_connections:
            return None
        
        if len(exec_connections) > 1:
            node_def = self.node_definition.get(node.name)
            node_label = node_def.label if node_def else node.name
            raise ValueError(
                f'Node "{node_label}" (ID: {node_id}) has multiple exec connections from pin "{pin_name}". '
                f'Each execution pin can only have one outgoing connection. '
                f'Please remove extra connections to resolve this issue.'
            )
        
        return self.node_map.get(exec_connections[0].to_node_id)
    
    def _collect_prepare(self, node_def: CodeckNodeDefinition) -> None:
        """Collect prepare items from a node definition.
        
        Args:
            node_def: The node definition to collect prepare items from
        """
        if node_def.prepare:
            for prep in node_def.prepare:
                # Use id() for efficient duplicate checking
                prep_id = id(prep)
                if prep_id not in self._prepare_ids:
                    self._prepare_ids.add(prep_id)
                    self.prepares.append(prep)
