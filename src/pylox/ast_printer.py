from pylox.expr import Expr, Binary, Grouping, Literal, Unary
from pylox.visitor import Visitor


class AstPrinter(Visitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *args):
        ast = f"({name}"

        for expr in args:
            ast += f" {expr.accept(self)}"

        ast += ")"

        return ast
        # Or a one-liner, but the former is more clear
        # return f"({name} {str([expr.accept(self).replace("'", "") for expr in args])[1:-1].replace(",", "").replace("'", "")})"


# For trying the ast printer
def main():
    from pylox.token import Token
    from pylox.token_type import TokenType

    expr: Binary = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123),
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal(45.67),
        ),
    )

    print(AstPrinter().print(expr))


if __name__ == "__main__":
    main()
