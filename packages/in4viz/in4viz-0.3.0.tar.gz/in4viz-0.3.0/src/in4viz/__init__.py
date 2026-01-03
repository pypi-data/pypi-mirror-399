"""
in4viz - ER図可視化ライブラリ

SVGとdraw.io形式での出力をサポートする統合ER図作成ライブラリ
"""

from .er_diagram import ERDiagram
from .core.models import Table, Column, LineType, Cardinality
from .backends.svg import SVGERDiagram
from .backends.drawio import DrawioERDiagram

__version__ = '0.1.1'

__all__ = [
    'ERDiagram',
    'Table',
    'Column',
    'LineType',
    'Cardinality',
    'SVGERDiagram',
    'DrawioERDiagram',
]
