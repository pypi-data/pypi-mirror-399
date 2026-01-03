from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from .expression import Expression


@dataclass(slots=True)
class ScopedExpression:
    """Represents an expression with captured context.

    Keeps track of the globals and locals from where the expression was created.
    """
    expression: Expression
    f_globals: dict[str, Any]
    f_locals: Mapping[str, Any]

    def replace(self, expression: Expression = None, f_globals=None, f_locals=None) -> Self:
        if not (expression is None or isinstance(expression, Expression)):
            raise TypeError("expression should be an Expression.")

        return ScopedExpression(
            expression if expression is not None else self.expression,
            f_globals if f_globals is not None else self.f_globals,
            f_locals if f_locals is not None else self.f_locals,
        )
