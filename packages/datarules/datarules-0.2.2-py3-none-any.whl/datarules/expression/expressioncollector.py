import ast


class ExpressionCollector(ast.NodeVisitor):
    def __init__(self):
        self.inputs = set()
        self.outputs = set()

    @property
    def variables(self):
        return self.inputs | self.outputs

    def visit_Name(self, node):
        self.generic_visit(node)
        if isinstance(node.ctx, ast.Store):
            self.outputs.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.inputs.add(node.id)

    def visit_AugAssign(self, node):
        # Tricky, but python marks it as store, so we need to add it to inputs ourselves.
        self.generic_visit(node)
        self.inputs.add(node.target.id)


def collect_expression(expr):
    parsed = ast.parse(str(expr))
    visitor = ExpressionCollector()
    visitor.visit(parsed)
    return visitor
