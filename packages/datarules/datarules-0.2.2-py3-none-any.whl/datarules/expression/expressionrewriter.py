import ast

import uneval


class ExpressionRewriter(ast.NodeTransformer):
    def visit_BoolOp(self, node):
        self.generic_visit(node)
        match node.op:
            case ast.And():
                res = node.values[0]
                for value in node.values[1:]:
                    res = ast.BinOp(res, ast.BitAnd(), value)
                return res
            case ast.Or():
                res = node.values[0]
                for value in node.values[1:]:
                    res = ast.BinOp(res, ast.BitOr(), value)
                return res

    def visit_BinOp(self, node):
        """Rewrite implies

        `a >> b` means `a` implies `b`.
        This is rewritten to (~a) | b

        `a << b` means `b` implies `a`.
        This is rewritten to a | ~b
        """
        self.generic_visit(node)
        match node.op:
            case ast.RShift():
                invert_left = ast.UnaryOp(ast.Invert(), node.left)
                return ast.BinOp(invert_left, ast.BitOr(), node.right)
            case ast.LShift():
                invert_right = ast.UnaryOp(ast.Invert(), node.right)
                return ast.BinOp(node.left, ast.BitOr(), invert_right)
            case _:
                return node

    def visit_Not(self, node):
        return ast.Invert()

    def visit_Compare(self, node):
        self.generic_visit(node)

        parts = []

        left = node.left

        for op, right in zip(node.ops, node.comparators):
            if isinstance(op, ast.In):
                part = ast.Call(ast.Attribute(value=left, attr="isin", ctx=ast.Load()),
                                args=[right], keywords=[])
            else:
                part = ast.Compare(left, [op], [right])
            parts.append(part)
            left = right

        res = parts[0]
        for value in parts[1:]:
            res = ast.BinOp(res, ast.BitAnd(), value)
        return res

    def visit_If(self, node):
        """Transform into `not test or body`."""
        self.generic_visit(node)
        body = node.body
        if len(body) == 1:
            [statement] = body
            return ast.BinOp(ast.UnaryOp(ast.Invert(), node.test), ast.BitOr(), statement)
        else:
            raise Exception("Multiline body is not supported.")

    def visit_IfExp(self, node):
        """Transform into `body.where(condition, else)`."""
        self.generic_visit(node)
        return ast.Call(ast.Attribute(value=node.body, attr="where", ctx=ast.Load()),
                        args=[node.test, node.orelse],
                        keywords=[])


def rewrite_expression(node):
    if isinstance(node, uneval.Expression):
        node = uneval.to_ast(node)
    rewritten = ExpressionRewriter().visit(node)
    ast.fix_missing_locations(rewritten)
    return ast.unparse(rewritten)


def main():
    expr = "if a > 2: h==3 and d<2"
    print(rewrite_expression(expr))

    # expr = "if a > 2: h==3 and d<2"
    # print(rewrite_expression(expr))

    expr = "width < height or width == height or width > height"
    print(rewrite_expression(expr))

    expr = "width < height > depth"
    print(rewrite_expression(expr))

    expr = "x in ['huis', 'boom', 'beest']"
    print(rewrite_expression(expr))

    expr = "x if x > 0 else -x"
    print(rewrite_expression(expr))


if __name__ == "__main__":
    main()
