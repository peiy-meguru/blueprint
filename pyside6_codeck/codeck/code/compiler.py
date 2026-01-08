"""Code compiler for generating JavaScript from blueprint."""

from typing import Optional
from ..store.node import NodeStore, CodeckNode, CodeckNodeDefinition, CodeImportPrepare, CodeFunctionPrepare
from ..store.connection import ConnectionStore, ConnectInfo
from ..store.variable import VariableStore
from ..utils.consts import STANDARD_PIN_EXEC_OUT
from ..utils.string_helper import format_function_indent


class CodeCompiler:
    """Compiler that generates JavaScript code from blueprint nodes."""
    
    def __init__(self):
        self.prepares: list = []
        self.module_type = 'esmodule'  # 'commonjs' or 'esmodule'
        self.use_skypack = False
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
                    code_text += f'// {node.id} (node: {definition.name})\n'
                
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
        """Generate variable declarations."""
        variables = list(self.variable_map.values())
        if not variables:
            return ''
        
        lines = []
        for var in variables:
            if var.default_value is None:
                lines.append(f'let {var.name};')
            else:
                import json
                lines.append(f'let {var.name} = {json.dumps(var.default_value)};')
        
        return '\n'.join(lines) + '\n\n'
    
    def _generate_prepare_code(self) -> str:
        """Generate prepare code (imports and functions)."""
        imports: dict[str, list[tuple[str, str]]] = {}
        functions: list[CodeFunctionPrepare] = []
        
        for item in self.prepares:
            if isinstance(item, CodeImportPrepare):
                if item.module not in imports:
                    imports[item.module] = []
                
                if item.member:
                    if isinstance(item.member, str):
                        member = (item.member, item.member)
                    else:
                        member = item.member
                    
                    # Deduplicate
                    if member not in imports[item.module]:
                        imports[item.module].append(member)
            
            elif isinstance(item, CodeFunctionPrepare):
                functions.append(item)
        
        prepare_code = ''
        
        # Generate imports
        if imports:
            import_lines = []
            for module, members in imports.items():
                if self.module_type == 'commonjs':
                    if not members:
                        import_lines.append(f"require('{module}');")
                    else:
                        for member in members:
                            if member[0] == '*':
                                import_lines.append(f"const {member[1]} = require('{module}');")
                            else:
                                import_lines.append(f"const {member[1]} = require('{module}').{member[0]};")
                else:
                    # ESModule
                    if self.use_skypack:
                        module_name = f'https://cdn.skypack.dev/{module}'
                    else:
                        module_name = module
                    
                    if not members:
                        import_lines.append(f"import '{module_name}';")
                    else:
                        member_strs = []
                        for member in members:
                            if member[0] != 'default' and member[0] == member[1]:
                                member_strs.append(str(member[0]))
                            else:
                                member_strs.append(f'{member[0]} as {member[1]}')
                        import_lines.append(f"import {{ {', '.join(member_strs)} }} from '{module_name}';")
            
            prepare_code += '\n'.join(import_lines) + '\n\n'
        
        # Generate functions
        if functions:
            func_lines = []
            for func in functions:
                params = ', '.join(func.parameters)
                body = format_function_indent(func.body, 2)
                func_lines.append(f'function {func.name}({params}) {{\n  {body}\n}}')
            
            prepare_code += '\n\n'.join(func_lines) + '\n\n'
        
        return prepare_code
    
    def _find_begin(self) -> CodeckNode:
        """Find the Begin node."""
        begin_nodes = [
            node for node in self.node_map.values()
            if self.node_definition.get(node.name, None) and 
               self.node_definition[node.name].type == 'begin'
        ]
        
        if not begin_nodes:
            raise ValueError('No Begin node found')
        
        if len(begin_nodes) > 1:
            raise ValueError('Multiple Begin nodes found')
        
        return begin_nodes[0]
    
    def _get_exec_next(self, node_id: str, pin_name: str = STANDARD_PIN_EXEC_OUT) -> Optional[CodeckNode]:
        """Get the next node connected to an exec pin."""
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
            raise ValueError(f'Node {node_id} has multiple exec connections from pin {pin_name}')
        
        return self.node_map.get(exec_connections[0].to_node_id)
    
    def _collect_prepare(self, node_def: CodeckNodeDefinition) -> None:
        """Collect prepare items from a node definition."""
        if node_def.prepare:
            self.prepares.extend(node_def.prepare)
