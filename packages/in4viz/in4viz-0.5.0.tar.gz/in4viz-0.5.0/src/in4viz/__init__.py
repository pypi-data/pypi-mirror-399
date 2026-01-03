"""
in4viz - ER図可視化ライブラリ

SVGとdraw.io形式での出力をサポートする統合ER図作成ライブラリ
"""

from .core.models import Table, Column, LineType, Cardinality
from .backends.svg import SVGERDiagram
from .backends.drawio import DrawioERDiagram

__version__ = '0.5.0'

__all__ = [
    'Table',
    'Column',
    'LineType',
    'Cardinality',
    'SVGERDiagram',
    'DrawioERDiagram',
]
