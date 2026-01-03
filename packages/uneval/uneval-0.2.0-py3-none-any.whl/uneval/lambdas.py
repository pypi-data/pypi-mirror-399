from .astbuild import to_ast
from .dsl import λ_, var, ExprType
from .evaluation import evaluate
from .scopedexpression import ScopedExpression


class _FunctionFactory:
    """Helper to create lambda-functions.

    The parameters of this function must be single-letters.
    """
    def __call__(self, expression: ExprType | ScopedExpression, **kwargs):
        """Create a lambda without parameters.

        >>> hello_world = F(to_ast("Hello World!"))
        >>> hello_world()
        "Hello World!"
        """
        return self._make((), expression, **kwargs)

    def __getattr__(self, item):
        """Create a lambda with single-letter parameters.
        >>> x, y = var.x, var.y
        >>> plus10 = F.x(x + 10)
        >>> plus10(5)
        15
        >>> multiply = F.xy(x * y)
        >>> multiply(5, 7)
        35
        """
        parameters = [var(p) for p in item]

        def accept_expression(expression: ExprType | ScopedExpression, **kwargs):
            return self._make(parameters, expression, **kwargs)

        return accept_expression

    @staticmethod
    def _make(parameters, expression, **kwargs):
        if isinstance(expression, ScopedExpression):
            λ_expr = expression.replace(expression=λ_((parameters), expression.expression))
        else:
            λ_expr = λ_(parameters, expression)

        return evaluate(λ_expr, **kwargs)

# λ is for naughty programmers. Use F for pep8-compliance.
F = λ = _FunctionFactory()
