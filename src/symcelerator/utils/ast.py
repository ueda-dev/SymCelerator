from __future__ import annotations
from typing import *
from ..pyobject.binomial import Binomial
from ..pyobject.symbol import Symbol
from ..pyobject.simplex import Simplex

class ConstNode(TypedDict):
    type: Literal['constant']
    value: int | float

class SymbolNode(TypedDict):
    type: Literal['symbol']
    position: int
    name: str
    desc: Optional[str]

class SimplexNode(TypedDict):
    type: Literal['simplex-node']
    operation: Literal['abs']
    value: ConstNode | SymbolNode | BinomialNode | SimplexNode

class BinomialNode(TypedDict):
    type: Literal['binomial-node']
    operation: Literal['add', 'sub', 'mul', 'truediv', 'floordiv', 'mod', 'divmod', 'pow']
    v1: ConstNode | SymbolNode | BinomialNode | SimplexNode
    v2: ConstNode | SymbolNode | BinomialNode | SimplexNode

NodeType:TypeAlias = ConstNode | SymbolNode | SimplexNode | BinomialNode

def get_ast_symbols(ast: dict) -> set:
    if ast['type'] == 'symbol':
        return {ast['name']}
    elif ast['type'] == 'binomial-node':
        return get_ast_symbols(ast['v1']) | (get_ast_symbols(ast['v2']) if 'v2' in ast else set())
    elif ast['type'] == 'simplex-node':
        return get_ast_symbols(ast['value'])
    return set()

def get_ast_symbols_v2(ast: Symbol | Binomial | Simplex) -> List[str]:
    symbols_dict: Dict[str, int] = {} #変数名:ポジション
    def get(node: Symbol | Binomial | Simplex):
        if type(node) == Symbol:
            symbols_dict[node._name] = node._position
        elif type(node) == Binomial:
            get(node._v1)
            get(node._v2)
        elif type(node) == Simplex:
            get(node._value)
        else:
            pass
    get(ast)
    symbols_list = list(symbols_dict.items())
    symbols_list.sort(key=lambda x:x[1])
    return [x[0] for x in symbols_list]


def generate_ast(obj: Binomial | Symbol | Simplex | int | float) -> NodeType:
    if type(obj) == Binomial:
        return {
            'type': 'binomial-node',
            'v1': generate_ast(obj._v1),
            'v2': generate_ast(obj._v2),
            'operation': obj._operation
        }
    
    elif type(obj) == Simplex:
        return {
            'type': 'simplex-node',
            'operation': obj._operation,
            'value': generate_ast(obj._value)
        }

    elif type(obj) == Symbol:
        return {
            'type': 'symbol',
            'position': obj._position,
            'name': obj._name,
            'desc': obj._desc
        }
    
    elif type(obj) == int or type(obj) == float:
        return {
            'type': 'constant',
            'value': obj
        }

    else:
        raise ValueError(f'ERROR: unsupported object type: {obj}')