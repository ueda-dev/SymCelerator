from __future__ import annotations
from typing import *
from .binomial import Binomial
from .simplex import Simplex

_T = TypeVar('_T')

class Symbol(Generic[_T]):
    DECLEARED_SYMBOLS = 0

    def __init__(self, name: str, dtype: Type[_T] | None = None, desc: str | None = None):
        self._position = Symbol.DECLEARED_SYMBOLS
        self._name = name
        self._dtype = dtype
        self._desc = desc
        Symbol.DECLEARED_SYMBOLS += 1

    #---特殊メソッド---
    def __repr__(self):
        return self._name
    
    def __add__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'add')

    def __radd__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'add')

    def __sub__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'sub')

    def __rsub__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'sub')

    def __mul__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'mul')

    def __rmul__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'mul')

    def __truediv__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'truediv')

    def __rtruediv__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'truediv')

    def __floordiv__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'floordiv')

    def __rfloordiv__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'floordiv')

    def __mod__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'mod')

    def __rmod__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'mod')

    def __divmod__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'divmod')

    def __rdivmod__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'divmod')

    def __pow__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(self, other, 'pow')

    def __rpow__(self, other: int | float | Binomial | Symbol | Simplex) -> Binomial:
        return Binomial(other, self,  'pow')

    def __neg__(self) -> Binomial:
        return self * (-1)

    def __pos__(self) -> Symbol:
        return self

    def __abs__(self) -> Simplex:
        return Simplex(self, 'abs')