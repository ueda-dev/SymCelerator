"""
Pythonで生成したASTを用いてPython関数を生成するモジュール  
AST生成機構のデバッグ用 & 他の言語でのパーサー作成の参考用
処理の流れは以下の手順に従う

式の生成 -> 関数定義構文の生成 -> 関数オブジェクト生成
"""

from typing import *
from ..utils.ast import get_ast_symbols
from ..utils.wrapper import PyFunctionWrapper, VectorizedPyFunctionWrapper

def generate_expr(ast: dict, prefix: str = '', suffix: str = '') -> str:
    match ast['type']:
        case 'binomial-node':
            match ast['operation']:
                case 'add':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} + {generate_expr(ast['v2'], prefix, suffix)})"
                case 'sub':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} - {generate_expr(ast['v2'], prefix, suffix)})"
                case 'mul':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} * {generate_expr(ast['v2'], prefix, suffix)})"
                case 'truediv':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} / {generate_expr(ast['v2'], prefix, suffix)})"
                case 'floordiv':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} // {generate_expr(ast['v2'], prefix, suffix)})"
                case 'mod':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} % {generate_expr(ast['v2'], prefix, suffix)})"
                case 'divmod':
                    return f"divmod({generate_expr(ast['v1'], prefix, suffix)}, {generate_expr(ast['v2'], prefix, suffix)})"
                case 'pow':
                    return f"({generate_expr(ast['v1'], prefix, suffix)} ** {generate_expr(ast['v2'], prefix, suffix)})"
                case _:
                    raise ValueError()

        case 'simplex-node':
           match ast['operation']:
               case 'abs':
                   return f'abs({generate_expr(ast["value"], prefix, suffix)})'
               case _:
                   raise ValueError()

        case 'symbol':
            return prefix + ast['name'] + suffix

        case 'constant':
            return ast['value']
        
def generate_function(ast: dict):
    expr = generate_expr(ast)
    code = f"lambda {','.join(get_ast_symbols(ast))} : {expr}"
    func_obj = eval(compile(code, '<symcelerator-gen-module>', 'eval'), {}, {})
    return PyFunctionWrapper(ast, func_obj)

def generate_vectorized_function(ast: dict):
    expr = generate_expr(ast, suffix='_i')
    symbols = get_ast_symbols(ast)
    code = f"lambda {','.join(symbols)}: [{expr} for {','.join([str(s) + '_i' for s in symbols])} in zip({','.join(symbols)})]"
    func_obj = eval(compile(code, '<symcelerator-gen-module>', 'eval'), {}, {})
    return VectorizedPyFunctionWrapper(ast, func_obj)
