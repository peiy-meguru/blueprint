"""String helper utilities."""

import uuid


def generate_node_id() -> str:
    """Generate a unique node ID."""
    return str(uuid.uuid4())[:8]


def format_function_indent(code: str | None, indent: int = 2) -> str:
    """Format code with proper indentation.
    
    Args:
        code: Code string to format (can be None)
        indent: Number of spaces for indentation
    
    Returns:
        Formatted code string with proper indentation
    """
    if not code:
        return ''
    
    lines = code.strip().split('\n')
    if not lines:
        return ''
    
    # Calculate minimum existing indentation
    min_indent = float('inf')
    for line in lines:
        if line.strip():  # Ignore empty lines
            stripped = len(line) - len(line.lstrip())
            min_indent = min(min_indent, stripped)
    
    if min_indent == float('inf'):
        min_indent = 0
    
    # Re-indent lines
    result_lines = []
    indent_str = ' ' * indent
    for line in lines:
        if line.strip():
            # Remove old indentation and add new
            result_lines.append(indent_str + line[min_indent:])
        else:
            result_lines.append('')
    
    return '\n'.join(result_lines)
