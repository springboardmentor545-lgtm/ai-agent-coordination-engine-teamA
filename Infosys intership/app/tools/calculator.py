import ast
import operator

from langchain_core.tools import tool


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def calculate(expression: str) -> float:
    """Safely evaluate a basic arithmetic expression."""

    if not expression or not expression.strip():
        raise ValueError("Expression cannot be empty.")

    try:
        tree = ast.parse(expression, mode="eval")
        return _evaluate(tree.body)
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.")
    except (SyntaxError, ValueError, TypeError):
        raise ValueError("Invalid arithmetic expression.")


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")

        return _OPERATORS[type(node.op)](left, right)

    raise ValueError("Only basic arithmetic operations are supported.")


@tool
def calculator_tool(expression: str) -> str:
    """Calculate a basic arithmetic expression."""

    try:
        return str(calculate(expression))
    except ValueError as exc:
        return f"Calculator error: {exc}"