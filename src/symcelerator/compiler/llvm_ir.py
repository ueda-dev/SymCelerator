from typing import *
from ..utils.ast import NodeType, get_ast_symbols_v2, generate_ast
from ..pyobject.symbol import Symbol
from ..pyobject.simplex import Simplex
from ..pyobject.binomial import Binomial

_VarName: TypeAlias = str
_Dtype: TypeAlias = Literal['double']

class TranspilerLLVM:
    def __init__(self, **arguments: _Dtype):
        self._arguments = arguments
        self._variables = 0
        self._code = ''

    def _generate_var_name(self) -> str:
        name = str(self._variables)
        self._variables += 1
        return name
    
    def const(self, value: int | float) -> _VarName:
        var_name = f'%{self._generate_var_name()}'
        self._code += f'{var_name} = add double 0.0, {value}\n'
        return var_name

    def call(self, func_name: str, arguments: Iterable[_VarName], dtype: str = 'double') -> _VarName:
        var_name = f'%{self._generate_var_name()}'
        args_str = ', '.join([f'{dtype} {arg}' for arg in arguments])
        self._code += f'{var_name} = call {dtype} @{func_name}({args_str})\n'
        return var_name
    
    def generate_llvm_code(self) -> str:
        header = f"define double @generated_fn({', '.join([f'double %{name}' for name in self._arguments.keys()])})"
        expressions = '{\n' + self._code + '  ret double %result\n}\n'
        return header + expressions

def generate_function(node: Simplex | Binomial | Symbol) -> str:
    ast = generate_ast(node)
    symbols = get_ast_symbols_v2(node)
    transpiler = TranspilerLLVM(**{name: 'double' for name in symbols})

    def gen(node: NodeType) -> _VarName:
        match node['type']:
            case 'constant':
                return transpiler.const(node['value'])
            case 'symbol':
                return f"%{node['name']}"
            case 'simplex-node':
                match node['operation']:
                    case 'abs':
                        operand = gen(node['value'])
                        return transpiler.call('fabs', [operand], dtype='double')
                    case _:
                        raise ValueError(f"Unsupported simplex-node operation: {node['operation']}")
            case 'binomial-node':
                match node['operation']:
                    case 'add':
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('fadd', [left, right], dtype='double')
                    case 'sub':
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('fsub', [left, right], dtype='double')
                    case 'mul':
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('fmul', [left, right], dtype='double')
                    case 'truediv':
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('fdiv', [left, right], dtype='double')
                    case 'floordiv':
                        # ここでは仮に通常のfdivを利用（本来は整数除算またはfloor関数の呼び出しが必要）
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('fdiv', [left, right], dtype='double')
                    case 'mod':
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('fmod', [left, right], dtype='double')
                    case 'divmod':
                        raise NotImplementedError("divmod operation is not implemented.")
                    case 'pow':
                        left = gen(node['v1'])
                        right = gen(node['v2'])
                        return transpiler.call('pow', [left, right], dtype='double')
                    case _:
                        raise ValueError(f"Unsupported binomial-node operation: {node['operation']}")
            case _:
                raise ValueError(f"Unsupported node type: {node['type']}")
    
    result_var = gen(ast)
    # 最終結果を%resultに代入
    transpiler._code += f"%result = add double 0.0, {result_var}\n"
    return transpiler.generate_llvm_code()
