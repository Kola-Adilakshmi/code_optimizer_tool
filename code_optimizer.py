
import ast
import operator

# Supported arithmetic operations
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

def evaluate_expression(expression, constants):
    """Evaluate safe arithmetic expressions and known constants."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return expression

    def simplify(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError("Unsupported constant")

        if isinstance(node, ast.Name):
            if node.id in constants:
                return constants[node.id]
            raise ValueError("Unknown variable")

        if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            value = simplify(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = simplify(node.left)
            right = simplify(node.right)
            return OPERATORS[type(node.op)](left, right)

        raise ValueError("Unsupported expression")

    try:
        value = simplify(tree.body)
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError):
        return expression


def optimize_code(source_code):
    constants = {}
    optimized = []

    for line in source_code.splitlines():
        line = line.strip()

        if not line or "=" not in line:
            if line:
                optimized.append(line)
            continue

        variable, expression = line.split("=", 1)
        variable = variable.strip()
        expression = expression.strip()

        # Simplify expressions using known constant values
        result = evaluate_expression(expression, constants)

        # Basic algebraic simplifications
        if result == expression:
            result = expression

        optimized.append(f"{variable} = {result}")

        # Record assignments that produce numeric constants
        try:
            value = ast.literal_eval(result)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                constants[variable] = value
            else:
                constants.pop(variable, None)
        except (ValueError, SyntaxError):
            constants.pop(variable, None)

    return optimized


if __name__ == "__main__":
    print("===== CODE OPTIMIZATION TOOL =====")
    print("Enter one assignment per line.")
    print("Enter a blank line to finish.\n")

    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)

    original = "\n".join(lines)
    result = optimize_code(original)

    print("\n--- Original Code ---")
    print(original)

    print("\n--- Optimized Code ---")
    print("\n".join(result))
