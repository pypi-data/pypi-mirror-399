from ...core.models import LineType, Cardinality


class DrawioEdge:
    """draw.io用のエッジ（関係線）クラス"""

    def __init__(self, from_node_id: str, to_node_id: str, line_type: LineType = LineType.STRAIGHT, cardinality: Cardinality = None):
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.line_type = line_type
        self.cardinality = cardinality if cardinality is not None else Cardinality()

    def _map_cardinality_to_arrow(self, cardinality_str: str) -> str:
        """
        カーディナリティ文字列をdraw.ioの矢印スタイルにマッピング

        Args:
            cardinality_str: カーディナリティ文字列（"1", "0..1", "*", etc.）

        Returns:
            draw.io矢印スタイル（ERone, ERmany, ERzeroToOne, etc.）
        """
        if cardinality_str in ["*", "1..*", "0..*", "0...*", "1...*", "many"]:
            return "ERmany"
        elif cardinality_str == "0..1":
            return "ERzeroToOne"
        elif cardinality_str == "0":
            return "ERzeroToOne"
        elif cardinality_str == "1" or not cardinality_str:
            return "ERone"
        else:
            return "ERone"

    def _build_edge_style(self) -> str:
        """
        エッジのスタイル文字列を構築

        Returns:
            draw.io用のスタイル文字列
        """
        style_parts = []

        # LineTypeに応じたedgeStyle
        if self.line_type == LineType.CRANK:
            style_parts.append("edgeStyle=orthogonalEdgeStyle")
            style_parts.append("rounded=0")
            style_parts.append("orthogonalLoop=1")
            style_parts.append("jettySize=auto")
        elif self.line_type == LineType.SPLINE:
            style_parts.append("edgeStyle=elbowEdgeStyle")
            style_parts.append("curved=1")
            style_parts.append("rounded=1")
        # STRAIGHTの場合はedgeStyleを省略

        # 基本スタイル
        style_parts.append("html=1")

        # カーディナリティから矢印スタイルを決定
        if self.cardinality:
            if self.cardinality.from_side:
                start_arrow = self._map_cardinality_to_arrow(self.cardinality.from_side)
                style_parts.append(f"startArrow={start_arrow}")

            if self.cardinality.to_side:
                end_arrow = self._map_cardinality_to_arrow(self.cardinality.to_side)
                style_parts.append(f"endArrow={end_arrow}")

        return ";".join(style_parts) + ";"

    def render_mxcell_data(self, from_cell_id: str, to_cell_id: str, edge_cell_id: str) -> dict:
        """
        エッジのmxCellデータを生成

        Args:
            from_cell_id: 開始ノードのmxCell ID
            to_cell_id: 終了ノードのmxCell ID
            edge_cell_id: エッジ自身のmxCell ID

        Returns:
            mxCellデータ辞書
        """
        from .generator import DrawioGenerator

        style = self._build_edge_style()
        return DrawioGenerator.create_edge_cell(
            cell_id=edge_cell_id,
            from_cell_id=from_cell_id,
            to_cell_id=to_cell_id,
            style=style
        )
