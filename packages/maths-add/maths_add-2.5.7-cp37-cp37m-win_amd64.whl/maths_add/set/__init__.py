# encoding:utf-8
from __future__ import annotations
from maths_add.except_error import decorate
from typing import Callable, Any
from maths_add.complex.comp import Complex
from fractions import Fraction
from typing import Union, Tuple

__all__ = [
    "Set"
]


def Print(is_print, A, B, string: str):
    if is_print:
        print(f"{A}{string}{B}")


def ERROR(args, typeList):
    for arg in args:
        is_valid = False
        for t in typeList:
            if t is type and isinstance(arg, type):
                is_valid = True
                break
            if isinstance(arg, t):
                is_valid = True
                break
        if not is_valid:
            raise TypeError(f"The arg must be one of the following types: {typeList}.")


class Set(object):
    """
        此类 Set 模拟
    """

    @decorate()
    def temp(self, B: Set):
        if B._Tp != self._Tp:
            raise TypeError("The set B's _Tp must be A's _Tp.")

    @decorate()
    def __init__(self, name: str, ve: tuple, _Tp: Union[type, Tuple[type, ...]]):
        ERROR([name], [str])
        ERROR([ve], [tuple])
        ERROR([_Tp], [type, tuple])
        self.name = name
        self.ve = ve
        self._Tp = _Tp

    @decorate()
    def __del__(self):
        print("对象被销毁")

    @decorate()
    def __str__(self):
        name = self.name
        s = str(self.ve)
        s = s.replace("(", "{")
        s = s.replace(")", "}")
        return f"{name} = " + s

    @decorate()
    def is_belong_to(self, element, is_print=True):
        if element in self.ve:
            Print(is_print, element, self.name, "∈")
            return True
        else:
            Print(is_print, element, self.name, "∉")
            return False

    @decorate()
    def is_a_subset_of(self, B: Set, is_print=True):
        ERROR([B], [Set])
        for element in B.ve:
            if not self.is_belong_to(element, is_print=False):
                Print(is_print, B.name, self.name, "⊈")
                return False
        Print(is_print, B.name, self.name, "⊆")
        return True

    @decorate()
    def union(self, B: Set):
        self.temp(B)
        C = Set("C", self.ve, self._Tp)
        for value in B.ve:
            if value in C.ve:
                continue
            else:
                new = list(C.ve)
                new.append(value)
                C.ve = tuple(new)
        return C

    @decorate()
    def intersection(self, B: Set):
        self.temp(B)
        C = Set("C", (), self._Tp)
        for value in B.ve:
            if value in self.ve:
                new = list(C.ve)
                new.append(value)
                C.ve = tuple(new)
            else:
                continue
        return C


class Standard_Set(object):

    @decorate()
    def __init__(self, name: str, lam: Callable[..., Any], _Tp: Union[type, Tuple[type, ...]]):
        ERROR([name], [str])
        ERROR([_Tp], [type, tuple])
        if not callable(lam):
            raise TypeError(f"The arg lam must be a Callable object (e.g. lambda function), got {type(lam)}.")
        self.name = name
        self.lam = lam
        self._Tp = _Tp

    @decorate()
    def is_belong_to(self, element, is_print=True):
        if self.lam(element):
            Print(is_print, element, self.name, "∈")
            return True
        else:
            Print(is_print, element, self.name, "∉")
            return False

    @decorate()
    def is_a_subset_of(self, B: Set, is_print=True):
        ERROR([B], [Set])
        for element in B.ve:
            if not self.is_belong_to(element, is_print=False):
                Print(is_print, B.name, self.name, "⊈")
                return False
        Print(is_print, B.name, self.name, "⊆")
        return True


def is_Q(x):
    try:
        Fraction(x)
    except Exception:
        return False
    return True


N = Standard_Set("N",
                 lambda x: True if (x >= 0 and type(x) == int) else False,
                 int)

Z = Standard_Set("Z",
                 lambda x: True if (type(x) == int) else False,
                 int)

Q = Standard_Set("Q",
                 is_Q,
                 (int, float))

R = Standard_Set("R",
                 lambda x: True if (isinstance(x, (int, float)) and not isinstance(x, Complex)) else False,
                 (int, float))

C = Standard_Set("C",
                 lambda x: True if (type(x) == Complex) else False,
                 Complex)

if __name__ == '__main__':
    '''
    s = Set("A", ("2", "FSDGJGssgf", "d"), str)
    s = s.intersection(Set("B", ("g", "f", "d"), str))
    print(s)
    c = Complex(3, 2)
    d = 1
    print(C.is_a_subset_of(Set("A", (c,), Complex)))
    '''
    S = Set("S", (1, 2, 3, 4, 5, 6, 7), int)
    S.is_a_subset_of(Set("A", (1, 2, 3), int))
