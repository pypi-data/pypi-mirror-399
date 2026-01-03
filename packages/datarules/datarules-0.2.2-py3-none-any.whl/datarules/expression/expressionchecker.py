import ast

import uneval


class ExpressionChecker(ast.NodeVisitor):
    """
    Quick safety analysis.

    This won't catch all problems. There are too many potential problems.
    Do not run on untrusted input.
    """
    def __init__(self):
        self.problems = []

    @property
    def variables(self):
        return self.inputs | self.outputs

    def visit_Name(self, node):
        if node.id.startswith("_") or node.id.startswith("func_"):
            self.problems.append(f"{node.id} is not allowed.")
        return self.generic_visit(node)

    def visit_While(self, node):
        self.problems.append("Whileloop is not permitted.")
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.problems.append("Function definition is not permitted.")
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.problems.append("Class definition is not permitted.")
        return self.generic_visit(node)

    def visit_Yield(self, node):
        self.problems.append("Generators are not permitted.")
        return self.generic_visit(node)

    def visit_YieldFrom(self, node):
        self.problems.append("Generators are not permitted.")
        return self.generic_visit(node)

    def visit_Lambda(self, node):
        self.problems.append("Lambdas are not permitted.")
        return self.generic_visit(node)


def check_expression(code):
    if isinstance(code, uneval.Expression):
        code = uneval.to_ast(code)
    node = ast.parse(code)
    visitor = ExpressionChecker()
    visitor.visit(node)
    return visitor
