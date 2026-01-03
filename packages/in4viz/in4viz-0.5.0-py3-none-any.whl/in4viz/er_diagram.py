"""ER図作成のための統合API"""
from typing import Union
from .core.models import Table, Column, LineType, Cardinality
from .backends.svg import SVGERDiagram
from .backends.drawio import DrawioERDiagram


class ERDiagram:
    """
    ER図作成のための統合クラス

    SVGまたはdraw.io形式での出力をサポート
    """

    def __init__(self, backend: str = 'svg', default_line_type: LineType = LineType.STRAIGHT):
        """
        ERDiagramを初期化

        Args:
            backend: 'svg' または 'drawio'
            default_line_type: デフォルトの線種
        """
        if backend == 'svg':
            self._diagram = SVGERDiagram(default_line_type)
        elif backend == 'drawio':
            self._diagram = DrawioERDiagram(default_line_type)
        else:
            raise ValueError(f"Unsupported backend: {backend}. Use 'svg' or 'drawio'.")

        self.backend = backend

    def add_table(self, table: Table, x: int = None, y: int = None) -> str:
        """
        テーブルを追加

        Args:
            table: Tableオブジェクト
            x, y: 座標（Noneの場合は自動配置）

        Returns:
            テーブルID（物理名）
        """
        return self._diagram.add_table(table, x, y)

    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None, cardinality: Cardinality = None):
        """
        エッジ（関係線）を追加

        Args:
            from_node_id: 開始テーブルID
            to_node_id: 終了テーブルID
            line_type: 線の種類
            cardinality: カーディナリティ
        """
        self._diagram.add_edge(from_node_id, to_node_id, line_type, cardinality)

    def set_node_position(self, node_id: str, x: int, y: int):
        """
        ノードの位置を設定

        Args:
            node_id: テーブルID
            x, y: 新しい座標
        """
        self._diagram.set_node_position(node_id, x, y)

    def save(self, output: Union[str, object]):
        """
        ファイルに保存

        Args:
            output: ファイルパス(str)またはファイルライクオブジェクト
        """
        if self.backend == 'svg':
            self._diagram.save_svg(output)
        elif self.backend == 'drawio':
            self._diagram.save_drawio(output)

    def render(self) -> str:
        """
        文字列として出力を生成

        Returns:
            SVG XML文字列またはdraw.io XML文字列
        """
        if self.backend == 'svg':
            return self._diagram.render_svg()
        elif self.backend == 'drawio':
            return self._diagram.render_drawio()
