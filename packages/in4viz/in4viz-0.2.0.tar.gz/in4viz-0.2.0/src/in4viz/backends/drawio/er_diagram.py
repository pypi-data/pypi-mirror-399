from typing import List, Dict, Tuple
from ...core.models import LineType, Cardinality, Table
from ...core.layout import LayoutEngine
from .canvas import DrawioCanvas, DrawioNode
from .stencil import DrawioTableStencil
from .rendering import DrawioEdge
from .generator import DrawioGenerator


class DrawioERDiagram:
    """draw.io形式でER図を生成するクラス"""

    def __init__(self, default_line_type: LineType = LineType.STRAIGHT):
        self.canvas = DrawioCanvas(default_line_type)
        self.nodes = self.canvas.nodes

    def add_table(self, table: Table, x: int = None, y: int = None) -> str:
        """
        テーブルを追加

        Args:
            table: Tableオブジェクト
            x, y: 座標（Noneの場合は自動配置）

        Returns:
            テーブルID（物理名）
        """
        table_id = table.name

        stencil = DrawioTableStencil()

        # Column dataclassをdict形式に変換
        columns_data = []
        for col in table.columns:
            columns_data.append({
                'name': col.name,
                'logical_name': col.logical_name,
                'type': col.type,
                'primary_key': col.primary_key,
                'nullable': col.nullable,
                'foreign_key': col.foreign_key,
                'index': col.index
            })

        data = {
            'table_name': table.name,
            'logical_name': table.logical_name,
            'columns': columns_data
        }

        # 幅を事前計算
        node_width = stencil.get_width(data)

        auto_positioned = (x is None or y is None)
        if auto_positioned:
            x, y = self._get_next_position()
            # 幅チェックして改行判定
            if x + node_width > self.canvas.width - 50:
                x = 50
                y += self.canvas.row_height
                self.canvas.next_position = [x, y]

        # ノードを作成（仮のcell_idで作成、後でステンシルから取得）
        node = DrawioNode(table_id, stencil, data, x, y, '')
        node.width = node_width
        self.canvas.add_node(node)

        # 次の配置位置を更新（自動配置の場合のみ）
        if auto_positioned:
            self._update_next_position(node_width)

        # キャンバスサイズを調整
        self._adjust_canvas_size_for_current_layout()

        return table_id

    def _get_next_position(self) -> Tuple[int, int]:
        """次の配置位置を取得"""
        x, y = self.canvas.next_position

        # 前回のノードの幅を考慮
        if self.nodes and x + 400 > self.canvas.width - 50:
            x = 50
            y += self.canvas.row_height

        self.canvas.next_position = [x, y]
        return x, y

    def _update_next_position(self, node_width: int):
        """次の配置位置を更新"""
        self.canvas.next_position[0] += node_width + 50

    def get_node(self, node_id: str) -> DrawioNode:
        """ノードを取得"""
        return self.canvas.get_node(node_id)

    def set_node_position(self, node_id: str, x: int, y: int):
        """ノードの位置を設定"""
        node = self.get_node(node_id)
        if node:
            node.x = x
            node.y = y

    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None, cardinality: Cardinality = None):
        """
        エッジ（関係線）を追加

        Args:
            from_node_id: 開始ノードID
            to_node_id: 終了ノードID
            line_type: 線の種類
            cardinality: カーディナリティ
        """
        edge = DrawioEdge(from_node_id, to_node_id, line_type or self.canvas.default_line_type, cardinality)
        self.canvas.edges.append(edge)
        # エッジ追加後にレイアウトを最適化
        self._optimize_layout_for_edges()

    def _optimize_layout_for_edges(self):
        """Force-directedアルゴリズムでレイアウト最適化"""
        if not self.canvas.edges:
            # エッジがない場合でもキャンバスサイズを調整
            self._adjust_canvas_size_for_current_layout()
            return

        # Force-directedレイアウトを実行
        new_width, new_height = LayoutEngine.layout(self.nodes, self.canvas.edges)

        # キャンバスサイズを更新
        self._update_canvas_size(new_width, new_height)

    def _adjust_canvas_size_for_current_layout(self):
        """現在のレイアウトに基づいてキャンバスサイズを調整"""
        new_width, new_height = LayoutEngine.adjust_canvas_size(self.nodes)
        self._update_canvas_size(new_width, new_height)

    def _update_canvas_size(self, width: int, height: int):
        """キャンバスサイズを更新"""
        self.canvas.width = width
        self.canvas.height = height

    def render_drawio(self) -> str:
        """
        draw.io XML形式でレンダリング

        Returns:
            mxGraphModel XML文字列
        """
        cells = []

        # ノード（テーブル）をレンダリング
        for node in self.nodes:
            # ステンシルからmxCellリストを取得
            table_cells, table_cell_id = node.stencil.render_mxcells(node.data, node.x, node.y, self.canvas)
            cells.extend(table_cells)
            # ノードにcell_idを設定（エッジで参照するため）
            node.cell_id = table_cell_id

        # エッジ（関係線）をレンダリング
        for edge in self.canvas.edges:
            from_node = self.get_node(edge.from_node_id)
            to_node = self.get_node(edge.to_node_id)

            if from_node and to_node:
                edge_cell_id = self.canvas.get_next_cell_id()
                edge_cell_data = edge.render_mxcell_data(from_node.cell_id, to_node.cell_id, edge_cell_id)
                cells.append(edge_cell_data)

        # mxGraphModel XMLを生成
        return DrawioGenerator.create_mxgraph_model(cells, self.canvas.width, self.canvas.height)

    def save_drawio(self, output):
        """
        draw.io XMLを出力する

        Args:
            output: ファイルパス(str)またはファイルライクオブジェクト
        """
        xml_content = self.render_drawio()

        if isinstance(output, str):
            # ファイルパスの場合
            with open(output, 'w', encoding='utf-8') as f:
                f.write(xml_content)
        else:
            # ストリームオブジェクトの場合
            output.write(xml_content)
