from typing import *
from ..utils.ast import get_ast_symbols_v2, NodeType, generate_ast
from ..pyobject.symbol import Symbol
from ..pyobject.simplex import Simplex
from ..pyobject.binomial import Binomial
import cppyy

def generate_cpp_code(node: Symbol | Simplex | Binomial, func_name:str = 'symcelerator_gen_fn'):
    def gen(ast: NodeType):
        match ast['type']:
            case 'constant':
                return ast['value']
            case 'symbol':
                return ast['name']
            case 'simplex-node':
                match ast['operation']:
                    case 'abs':
                        return f'std::fabs({gen(ast["value"])})'
                    case _:
                        raise NotImplementedError(f'operation {ast['operation']} is not supported')
            case 'binomial-node':
                left = gen(ast['v1'])
                right = gen(ast['v2'])
                match ast['operation']:
                    case 'add':
                        return f'({left} + {right})'
                    case 'sub':
                        return f'({left} - {right})'
                    case 'mul':
                        return f'({left} * {right})'
                    case 'truediv':
                        return f'({left} / {right})'
                    case 'floordiv':
                        return f'std::floor({left} / {right})'
                    case 'mod':
                        return f'std::fmod({left}, {right})'
                    case 'pow':
                        return f'std::pow({left}, {right})'
                    case 'divmod':
                        raise NotImplementedError(f'divmod operation is not supported')
                    case _:
                        raise ValueError(f'unsupporte operand {ast['operation']}')

            case _:
                raise ValueError()

    ast = generate_ast(node)
    symbols = get_ast_symbols_v2(node)
    expressions = gen(ast)
    args = ', '.join([f'double {name}' for name in symbols])
    code = f"""\
#include <cmath>

extern "C" double {func_name}({args}) {{
return {expressions};
}}
"""
    return code

def generate_cpp_vectorized_code(node: Symbol | Simplex | Binomial, func_name: str):
    # ベクトル化されていない関数の定義
    loop_target_name = f'{func_name}_{id(node)}'
    loop_target_src = generate_cpp_code(node, loop_target_name)

    # ベクトル化のためのラッパー部分の実装
    wrapper_format = f"""
#include <iostream>
#include <vector>
#include <stdexcept>
{loop_target_src}

template<typename T, typename... Args>
std::vector<double> {func_name}(const std::vector<T>& first, const Args&... args)""" + """ {
    size_t size = first.size();
    if (((args.size() != size) || ...)) {
        throw std::invalid_argument("All arrays must have the same length.");
    }

    std::vector<double> results(size);

    for (size_t i = 0; i < size; ++i) {
        results[i] = """ + f"{loop_target_name}(first[i], (args[i])...)" + """;
    }

    return results;
}

""" + f"template std::vector<double> {func_name}(const std::vector<double>&, const std::vector<double>&, const std::vector<double>&);"
    return wrapper_format

def generate_function(node: Symbol | Simplex | Binomial):
    name = f'symcelerator_gen_fn_{id(node)}'
    code = generate_cpp_code(node, name)
    cppyy.cppdef(code)
    func = getattr(cppyy.gbl, name)
    return func

def generate_vectorized_function(node: Symbol | Simplex | Binomial):
    name = 'symcelerator_gen_fn'
    code = generate_cpp_vectorized_code(node, name)
    cppyy.cppdef(code)
    func = getattr(cppyy.gbl, name)
    return func