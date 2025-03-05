from typing import *
from io import BytesIO
import matplotlib.pyplot as plt

class PyFunctionWrapper:
    def __init__(self, ast: dict, callable_object: Callable):
        self._ast = ast
        self._callable = callable_object

    def __call__(self, *args: Any, **kwds: Any) -> int | float:
        return self._callable(*args, **kwds)

    #---ドキュメント生成ユーティリティ---
    def latex(self) -> str:
        """
        returns LaTeX-string
        """
        def ast_to_latex(ast: dict) -> str:
            match ast['type']:
                case 'binary-node':
                    match ast['operation']:
                        case 'add':
                            return f"{ast_to_latex(ast['v1'])} + {ast_to_latex(ast['v2'])}"
                        case 'sub':
                            return f"{ast_to_latex(ast['v1'])} - {ast_to_latex(ast['v2'])}"
                        case 'mul':
                            return f"{ast_to_latex(ast['v1'])} \\times {ast_to_latex(ast['v2'])}"
                        case 'truediv':
                            return f"\\frac{{{ast_to_latex(ast['v1'])}}}{{{ast_to_latex(ast['v2'])}}}"
                        case 'pow':
                            return f"{ast_to_latex(ast['v1'])}^{{{ast_to_latex(ast['v2'])}}}"
                        case _:
                            raise ValueError()

                case 'simplex-node':
                    match ast['operation']:
                        case 'abs':
                            return f"\\left|{ast_to_latex(ast['value'])}\\right|"
                        case _:
                            raise ValueError()

                case 'symbol':
                    return ast['name']

                case 'constant':
                    return str(ast['value'])

        def generate_latex(ast: dict) -> str:
            return f"$$ {ast_to_latex(ast)} $$"

        return generate_latex(self._ast)

    def _image(self, fmt: Literal['png', 'svg']) -> bytes:
        def latex_to_png(latex_expr: str):
            with BytesIO() as buff:
                fig, ax = plt.subplots()
                ax.text(0.5, 0.5, f"${latex_expr}$", fontsize=20, ha='center', va='center')
                ax.axis("off")
                fig.savefig(buff, bbox_inches='tight', dpi=300, format=fmt)
                plt.close(fig)
                return buff.read()
        return latex_to_png(self.latex())

    def png(self) -> bytes:
        return self._image('png')

    def svg(self) -> bytes:
        return self._image('svg')

class VectorizedPyFunctionWrapper(PyFunctionWrapper):
    """
    ベクトル化した関数オブジェクトを生成したときはこちらを利用する。
    機能面で特に変化は無し（型注釈が変わるだけ）
    """
    def __call__(self, *args:Iterable[Any], **kwds:Iterable[Any]) -> List[int | float]:
        return super().__call__(*args, **kwds)