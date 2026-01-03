from typing import List, Dict, Any
from ...core.models import LineType


class DrawioCanvas:
    """draw.io用のキャンバス管理クラス"""

    def __init__(
        self,
        default_line_type: LineType = LineType.STRAIGHT,
        width: int = 1200,
        height: int = 800
    ):
        self.width = width
        self.height = height
        self.default_line_type = default_line_type
        self.nodes: List['DrawioNode'] = []
        self.edges: List = []
        self.next_position = [50, 50]
        self.column_width = 450
        self.row_height = 200
        self.next_cell_id = 2

    def get_next_cell_id(self) -> str:
        """次のmxCell IDを取得"""
        cell_id = str(self.next_cell_id)
        self.next_cell_id += 1
        return cell_id

    def add_node(self, node: 'DrawioNode'):
        """ノードを追加"""
        self.nodes.append(node)

    def get_node(self, node_id: str) -> 'DrawioNode':
        """ノードIDからノードを取得"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None


class DrawioNode:
    """draw.io用のノード（テーブル）を表すクラス"""

    def __init__(self, node_id: str, stencil, data: Dict[str, Any], x: int, y: int, cell_id: str):
        self.node_id = node_id
        self.cell_id = cell_id
        self.stencil = stencil
        self.data = data
        self.x = x
        self.y = y
        self.width = self._calculate_width()
        self.height = self._calculate_height()

    def _calculate_height(self) -> int:
        """高さを計算"""
        if hasattr(self.stencil, 'calculate_height'):
            return self.stencil.calculate_height(self.data)
        return 100

    def _calculate_width(self) -> int:
        """幅を計算"""
        if hasattr(self.stencil, 'get_width'):
            return self.stencil.get_width(self.data)
        return 200
