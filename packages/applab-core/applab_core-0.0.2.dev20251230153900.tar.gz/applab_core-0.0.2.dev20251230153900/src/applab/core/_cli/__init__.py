"""applab/__init__.py：包入口模块.

提供包的入口函数，并导入包中的核心功能模块。
"""

__all__ = []


from typing import Protocol


class BaseProto(Protocol):
    a: int  # fine (explicitly declared as `int`)

    def method_member(self) -> int: ...  # fine: a method definition using `def` is considered a declaration

    c = "some variable"  # error: no explicit declaration, leading to ambiguity
    b = method_member  # error: no explicit declaration, leading to ambiguity

    # error: this creates implicit assignments of `d` and `e` in the protocol class body.
    # Were they really meant to be considered protocol members?
    for d, e in enumerate(range(42)):
        pass


class SubProto(BaseProto, Protocol):
    a = 42  # fine (declared in superclass)
