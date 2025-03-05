from .utils.wrapper import PyFunctionWrapper, VectorizedPyFunctionWrapper
from .utils.ast import generate_ast
from .pyobject.symbol import Symbol
from .pyobject.simplex import Simplex
from .pyobject.binomial import Binomial
from .utils.languages import SupportedLanguages

def symcelerate(node: Symbol | Simplex | Binomial, lang: SupportedLanguages = 'c') -> PyFunctionWrapper:
    ast = generate_ast(node)
    match lang:
        case 'python':
            from .compiler.python import generate_function
            return PyFunctionWrapper(ast, generate_function(ast))
        case 'c':
            from .compiler.cpp import generate_function
            return PyFunctionWrapper(ast, generate_function(node))
        case _:
            raise ValueError(f'unsupported lang {lang}')

def symcelerate_vectorized(node: Symbol | Simplex | Binomial, lang: SupportedLanguages = 'c') -> VectorizedPyFunctionWrapper:
    ast = generate_ast(node)
    match lang:
        case 'python':
            from .compiler.python import generate_vectorized_function
            return VectorizedPyFunctionWrapper(ast, generate_vectorized_function(ast))
        case 'c':
            from .compiler.cpp import generate_vectorized_function
            return VectorizedPyFunctionWrapper(ast, generate_vectorized_function(ast))
        case _:
            raise ValueError(f'unsupported lang {lang}')