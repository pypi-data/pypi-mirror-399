import ast
from functools import singledispatch


# Use of singledispatch is just an implementation detail (don't register other)
@singledispatch
def to_ast(node):
    if dunder := getattr(node, "__ast__", None):
        return dunder()
    else:
        raise TypeError(f"Unsupported type: {type(node)}")


@to_ast.register
def _(node: ast.AST):
    return node


@to_ast.register(int)
@to_ast.register(float)
@to_ast.register(bool)
@to_ast.register(bytes)
@to_ast.register(bytearray)
@to_ast.register(str)
@to_ast.register(complex)
@to_ast.register(type(None))
@to_ast.register(type(...))
def _(node):
    return ast.Constant(node)


@to_ast.register
def _(node: tuple):
    return ast.Tuple(elts=[to_ast(x) for x in node], ctx=ast.Load())


@to_ast.register
def _(node: list):
    return ast.List(elts=[to_ast(x) for x in node], ctx=ast.Load())


@to_ast.register
def _(node: set):
    return ast.Set(elts=[to_ast(x) for x in node])


@to_ast.register
def _(node: dict):
    return ast.Dict(keys=[to_ast(k) for k in node.keys()],
                    values=[to_ast(v) for v in node.values()])


@to_ast.register
def _(node: slice):
    return ast.Slice(to_ast(node.start), to_ast(node.stop), to_ast(node.step))


@to_ast.register
def _(node: range):
    args = [to_ast(node.start), to_ast(node.stop), to_ast(node.step)]
    return ast.Call(ast.Name('range', ctx=ast.Load()), args=args, keywords=[])


@to_ast.register
def _(node: frozenset):
    mutable_set = ast.Set(elts=[to_ast(x) for x in node])
    ast.Call(ast.Name('frozenset', ctx=ast.Load()), args=[mutable_set], keywords=[])
