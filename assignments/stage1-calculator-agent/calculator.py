"""
Safe calculator tool for agent.
"""
import ast
import operator


# Allowed operations
ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: Mathematical expression string (e.g., "23 * 17 + 5")

    Returns:
        Result as string, or error message

    Examples:
        >>> calculator("2 + 3")
        '5'
        >>> calculator("10 / 2")
        '5.0'
    """
    try:
        # Parse expression into AST
        tree = ast.parse(expression, mode='eval')

        # Evaluate using whitelist
        result = _eval_node(tree.body)
        return str(result)

    except (SyntaxError, ValueError, TypeError, KeyError) as e:
        return f"Error: Invalid expression - {str(e)}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"


def _eval_node(node):
    """Recursively evaluate AST node with whitelist."""
    if isinstance(node, ast.Constant):  # Numbers
        return node.value

    elif isinstance(node, ast.BinOp):  # Binary operations
        op_type = type(node.op)
        if op_type not in ALLOWED_OPS:
            raise ValueError(f"Operation {op_type.__name__} not allowed")

        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return ALLOWED_OPS[op_type](left, right)

    elif isinstance(node, ast.UnaryOp):  # Unary operations (e.g., -5)
        op_type = type(node.op)
        if op_type not in ALLOWED_OPS:
            raise ValueError(f"Operation {op_type.__name__} not allowed")

        operand = _eval_node(node.operand)
        return ALLOWED_OPS[op_type](operand)

    else:
        raise ValueError(f"Node type {type(node).__name__} not allowed")
