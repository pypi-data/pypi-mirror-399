import ast
from collections import ChainMap
from types import CodeType
from typing import Any

from .expression import Expression
from .dsl import expr, ExprType
from .scopedexpression import ScopedExpression


def compiled(obj: ExprType | CodeType, /) -> Any:
    """Compile the given expression.

    If expression is an Expression, the result is memoized.
    Similar to built-in function compile, but specialized for Expression and always sets `mode="eval"`.

    If obj is a ScopedExpression, use `compiled(expr(scoped_expr))` instead.
    """
    match obj:
        case Expression():
            return obj._compile()
        case CodeType():
            return obj
        case str() | ast.AST():
            return expr(obj)._compile()
        case _:
            raise TypeError(f"{type(obj)} is not an Expression.")


def evaluate(obj: ExprType | CodeType | ScopedExpression, data=None, /, **kwargs) -> Any:
    """Evaluate the expression.

    Similar to built-in function eval, but specialized to work with Expression.
    """
    if isinstance(obj, ScopedExpression):
        data = ChainMap(data, obj.f_globals) if data else obj.f_globals
        if kwargs is None:
            kwargs = obj.f_locals
        else:
            kwargs.update(obj.f_locals)
        obj = obj.expression

    return eval(compiled(obj), kwargs, data or {})
