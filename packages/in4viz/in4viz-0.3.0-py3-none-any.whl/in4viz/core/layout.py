"""Force-directedレイアウトアルゴリズム

ノード間の斥力とエッジの引力をシミュレートして
自然で美しいレイアウトを生成する
"""
from typing import List, Dict, Tuple, Protocol, Set
from collections import defaultdict
import math


class LayoutNode(Protocol):
    """レイアウト計算用のノードプロトコル"""
    node_id: str
    x: int
    y: int
    width: int
    height: int


class LayoutEdge(Protocol):
    """レイアウト計算用のエッジプロトコル"""
    from_node_id: str
    to_node_id: str


class LayoutEngine:
    """
    Force-directedレイアウトエンジン

    接続されたノードを近くに配置し、
    重なりを解消して見やすいレイアウトを生成する
    """

    @staticmethod
    def layout(
        nodes: List[LayoutNode],
        edges: List[LayoutEdge],
        iterations: int = 200,
        margin: int = 50,
        min_width: int = 800,
        min_height: int = 600
    ) -> Tuple[int, int]:
        """
        Force-directedアルゴリズムでノードを配置

        Args:
            nodes: レイアウト対象のノードリスト
            edges: エッジリスト
            iterations: シミュレーション反復回数
            margin: キャンバス端のマージン
            min_width: キャンバスの最小幅（デフォルト: 800）
            min_height: キャンバスの最小高さ（デフォルト: 600）

        Returns:
            (canvas_width, canvas_height)
        """
        if not nodes:
            return min_width, min_height

        n = len(nodes)
        node_map = {node.node_id: node for node in nodes}

        # 接続情報を構築
        neighbors = defaultdict(set)
        degree = defaultdict(int)
        for edge in edges:
            if edge.from_node_id in node_map and edge.to_node_id in node_map:
                neighbors[edge.from_node_id].add(edge.to_node_id)
                neighbors[edge.to_node_id].add(edge.from_node_id)
                degree[edge.from_node_id] += 1
                degree[edge.to_node_id] += 1

        # 接続されたノードと孤立ノードを分離
        connected_nodes = [node for node in nodes if degree.get(node.node_id, 0) > 0]
        isolated_nodes = [node for node in nodes if degree.get(node.node_id, 0) == 0]

        # ノードサイズの平均
        avg_width = sum(node.width for node in nodes) / n
        avg_height = sum(node.height for node in nodes) / n

        # 理想的なエッジ長（接続ノード間の距離）
        ideal_length = max(avg_width, avg_height) * 1.8

        # 接続されたノードのみで初期配置とシミュレーション
        if connected_nodes:
            connected_node_map = {node.node_id: node for node in connected_nodes}

            # 初期配置: 接続の多いノードを中心に配置（接続ノードのみ）
            positions = LayoutEngine._initial_placement(
                connected_nodes, neighbors, degree, ideal_length, margin
            )

            # Force-directed simulation（接続ノードのみ）
            positions = LayoutEngine._force_directed_simulation(
                positions, connected_node_map, edges, neighbors, ideal_length, iterations
            )

            # 重なり解消（接続ノードのみ）
            positions = LayoutEngine._resolve_overlaps(positions, connected_node_map, 30)

            # 孤立ノードをシミュレーション後に配置
            if isolated_nodes:
                positions = LayoutEngine._place_isolated_nodes(
                    positions, isolated_nodes, ideal_length
                )
        else:
            # 全ノードが孤立している場合はグリッド配置
            positions = LayoutEngine._grid_placement(nodes, ideal_length, margin)

        # 重なり解消
        positions = LayoutEngine._resolve_overlaps(positions, node_map, 30)

        # 座標を正規化（左上をmarginに）
        min_x = min(pos[0] - node_map[nid].width / 2 for nid, pos in positions.items())
        min_y = min(pos[1] - node_map[nid].height / 2 for nid, pos in positions.items())

        max_width = 0
        max_height = 0

        for node in nodes:
            cx, cy = positions[node.node_id]
            node.x = int(cx - node.width / 2 - min_x + margin)
            node.y = int(cy - node.height / 2 - min_y + margin)

            max_width = max(max_width, node.x + node.width)
            max_height = max(max_height, node.y + node.height)

        # 計算されたサイズと最低サイズの大きい方を採用
        calculated_width = max_width + margin
        calculated_height = max_height + margin

        return max(calculated_width, min_width), max(calculated_height, min_height)

    @staticmethod
    def _initial_placement(
        nodes: List[LayoutNode],
        neighbors: Dict[str, Set[str]],
        degree: Dict[str, int],
        ideal_length: float,
        margin: int
    ) -> Dict[str, List[float]]:
        """接続構造に基づく初期配置"""
        positions: Dict[str, List[float]] = {}

        # 接続されたノードと孤立ノードを分離
        connected_nodes = [n for n in nodes if degree.get(n.node_id, 0) > 0]
        isolated_nodes = [n for n in nodes if degree.get(n.node_id, 0) == 0]

        # 接続されたノードがない場合は、全ノードをグリッド配置
        if not connected_nodes:
            return LayoutEngine._grid_placement(nodes, ideal_length, margin)

        # 接続されたノードを次数でソート（多いものから配置）
        sorted_connected = sorted(connected_nodes, key=lambda x: -degree.get(x.node_id, 0))
        n_connected = len(sorted_connected)

        # 最初のノード（最も接続の多いノード）を中心に
        center = ideal_length * math.sqrt(n_connected) / 2 + margin

        placed: Set[str] = set()
        for i, node in enumerate(sorted_connected):
            if i == 0:
                # 中心に配置
                positions[node.node_id] = [center, center]
                placed.add(node.node_id)
            else:
                # 既に配置された隣接ノードの近くに配置
                neighbor_positions = [
                    positions[nid] for nid in neighbors[node.node_id]
                    if nid in placed
                ]

                if neighbor_positions:
                    # 隣接ノードの重心を計算
                    avg_x = sum(p[0] for p in neighbor_positions) / len(neighbor_positions)
                    avg_y = sum(p[1] for p in neighbor_positions) / len(neighbor_positions)

                    # 重心から少しずらした位置に配置
                    angle = 2 * math.pi * i / n_connected
                    positions[node.node_id] = [
                        avg_x + ideal_length * 0.8 * math.cos(angle),
                        avg_y + ideal_length * 0.8 * math.sin(angle)
                    ]
                else:
                    # 隣接ノードが未配置なら、中心の周りに配置
                    angle = 2 * math.pi * i / n_connected
                    radius = ideal_length * (1 + i / n_connected)
                    positions[node.node_id] = [
                        center + radius * math.cos(angle),
                        center + radius * math.sin(angle)
                    ]
                placed.add(node.node_id)

        # 孤立ノードを接続グループの端に配置
        if isolated_nodes:
            positions = LayoutEngine._place_isolated_nodes(
                positions, isolated_nodes, ideal_length
            )

        return positions

    @staticmethod
    def _grid_placement(
        nodes: List[LayoutNode],
        ideal_length: float,
        margin: int
    ) -> Dict[str, List[float]]:
        """全ノードが孤立している場合のグリッド配置"""
        positions: Dict[str, List[float]] = {}
        n = len(nodes)
        cols = max(1, int(math.sqrt(n)))

        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            positions[node.node_id] = [
                margin + col * ideal_length * 1.5,
                margin + row * ideal_length * 1.5
            ]

        return positions

    @staticmethod
    def _place_isolated_nodes(
        positions: Dict[str, List[float]],
        isolated_nodes: List[LayoutNode],
        ideal_length: float
    ) -> Dict[str, List[float]]:
        """孤立ノードを接続グループの端に配置"""
        if not positions:
            return positions

        # 接続グループの境界を計算
        min_x = min(p[0] for p in positions.values())
        max_x = max(p[0] for p in positions.values())
        min_y = min(p[1] for p in positions.values())
        max_y = max(p[1] for p in positions.values())

        # 孤立ノードをグループの右側に縦に並べる
        start_x = max_x + ideal_length * 1.2
        start_y = min_y

        for i, node in enumerate(isolated_nodes):
            positions[node.node_id] = [
                start_x,
                start_y + i * ideal_length * 0.8
            ]

        return positions

    @staticmethod
    def _force_directed_simulation(
        positions: Dict[str, List[float]],
        node_map: Dict[str, LayoutNode],
        edges: List[LayoutEdge],
        neighbors: Dict[str, Set[str]],
        ideal_length: float,
        iterations: int
    ) -> Dict[str, List[float]]:
        """Force-directedシミュレーション"""
        positions = {k: list(v) for k, v in positions.items()}
        n = len(positions)

        if n <= 1:
            return positions

        # パラメータ
        k = ideal_length  # 理想距離
        temperature = k * 2  # 初期温度
        min_temp = 1.0

        for _ in range(iterations):
            forces: Dict[str, List[float]] = {nid: [0.0, 0.0] for nid in positions}

            # 斥力（全ノード間）
            node_ids = list(positions.keys())
            for i, nid1 in enumerate(node_ids):
                for nid2 in node_ids[i + 1:]:
                    dx = positions[nid1][0] - positions[nid2][0]
                    dy = positions[nid1][1] - positions[nid2][1]
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.1

                    # 斥力: k^2 / dist（遠いノードには弱い斥力）
                    repulsion = (k * k) / dist * 0.5

                    fx = (dx / dist) * repulsion
                    fy = (dy / dist) * repulsion

                    forces[nid1][0] += fx
                    forces[nid1][1] += fy
                    forces[nid2][0] -= fx
                    forces[nid2][1] -= fy

            # 引力（接続ノード間）- より強い引力
            for edge in edges:
                nid1, nid2 = edge.from_node_id, edge.to_node_id
                if nid1 not in positions or nid2 not in positions:
                    continue

                dx = positions[nid2][0] - positions[nid1][0]
                dy = positions[nid2][1] - positions[nid1][1]
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < 0.1:
                    continue

                # 引力: dist^2 / k（強い引力で接続ノードを近づける）
                attraction = (dist * dist) / k * 1.5

                fx = (dx / dist) * attraction
                fy = (dy / dist) * attraction

                forces[nid1][0] += fx
                forces[nid1][1] += fy
                forces[nid2][0] -= fx
                forces[nid2][1] -= fy

            # 位置更新
            for nid in positions:
                fx, fy = forces[nid]
                force_mag = math.sqrt(fx * fx + fy * fy)
                if force_mag > 0.1:
                    # 温度で移動量を制限
                    scale = min(force_mag, temperature) / force_mag
                    positions[nid][0] += fx * scale
                    positions[nid][1] += fy * scale

            # 冷却
            temperature = max(temperature * 0.95, min_temp)

        return positions

    @staticmethod
    def _resolve_overlaps(
        positions: Dict[str, List[float]],
        node_map: Dict[str, LayoutNode],
        min_gap: int,
        iterations: int = 100
    ) -> Dict[str, List[float]]:
        """ノードの重なりを解消"""
        positions = {k: list(v) for k, v in positions.items()}

        for _ in range(iterations):
            moved = False
            node_ids = list(positions.keys())

            for i, nid1 in enumerate(node_ids):
                for nid2 in node_ids[i + 1:]:
                    n1 = node_map[nid1]
                    n2 = node_map[nid2]

                    x1, y1 = positions[nid1]
                    x2, y2 = positions[nid2]

                    # 必要な最小距離
                    min_dx = (n1.width + n2.width) / 2 + min_gap
                    min_dy = (n1.height + n2.height) / 2 + min_gap

                    dx = abs(x2 - x1)
                    dy = abs(y2 - y1)

                    # 重なり判定（矩形の重なり）
                    if dx < min_dx and dy < min_dy:
                        moved = True
                        overlap_x = min_dx - dx
                        overlap_y = min_dy - dy

                        # 最小の移動で解消
                        if overlap_x < overlap_y:
                            push = overlap_x / 2 + 1
                            if x1 < x2:
                                positions[nid1][0] -= push
                                positions[nid2][0] += push
                            else:
                                positions[nid1][0] += push
                                positions[nid2][0] -= push
                        else:
                            push = overlap_y / 2 + 1
                            if y1 < y2:
                                positions[nid1][1] -= push
                                positions[nid2][1] += push
                            else:
                                positions[nid1][1] += push
                                positions[nid2][1] -= push

            if not moved:
                break

        return positions

    @staticmethod
    def adjust_canvas_size(
        nodes: List[LayoutNode],
        margin: int = 50,
        min_width: int = 800,
        min_height: int = 600
    ) -> Tuple[int, int]:
        """現在のレイアウトに基づいてキャンバスサイズを計算"""
        if not nodes:
            return min_width, min_height

        max_width = 0
        max_height = 0

        for node in nodes:
            max_width = max(max_width, node.x + node.width)
            max_height = max(max_height, node.y + node.height)

        # 計算されたサイズと最低サイズの大きい方を採用
        calculated_width = max_width + margin
        calculated_height = max_height + margin

        return max(calculated_width, min_width), max(calculated_height, min_height)
