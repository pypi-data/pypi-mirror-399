import xml.etree.ElementTree as ET
from typing import List, Dict, Any


class DrawioGenerator:
    """draw.io (mxGraph) XML生成ユーティリティ - テーブル形式"""

    @staticmethod
    def create_mxgraph_model(cells: List[Dict[str, Any]], width: int = 1200, height: int = 800) -> str:
        """
        mxGraphModelのXML文字列を生成

        Args:
            cells: mxCellのデータリスト
            width: キャンバス幅
            height: キャンバス高さ

        Returns:
            XML文字列（非圧縮形式）
        """
        root = ET.Element('mxGraphModel')
        root.set('dx', '1106')
        root.set('dy', '776')
        root.set('grid', '1')
        root.set('gridSize', '10')
        root.set('guides', '1')
        root.set('tooltips', '1')
        root.set('connect', '1')
        root.set('arrows', '1')
        root.set('fold', '1')
        root.set('page', '1')
        root.set('pageScale', '1')
        root.set('pageWidth', str(width))
        root.set('pageHeight', str(height))
        root.set('math', '0')
        root.set('shadow', '0')

        root_elem = ET.SubElement(root, 'root')

        # デフォルトセル（id=0, 1）
        cell0 = ET.SubElement(root_elem, 'mxCell')
        cell0.set('id', '0')

        cell1 = ET.SubElement(root_elem, 'mxCell')
        cell1.set('id', '1')
        cell1.set('parent', '0')

        # 各セルを追加
        for cell_data in cells:
            DrawioGenerator._create_cell_element(root_elem, cell_data)

        # XML文字列に変換（整形付き）
        ET.indent(root, space='  ', level=0)
        return ET.tostring(root, encoding='unicode')

    @staticmethod
    def _create_cell_element(parent: ET.Element, cell_data: Dict[str, Any]):
        """
        mxCell要素を生成

        Args:
            parent: 親XML要素
            cell_data: セルのデータ辞書
        """
        cell = ET.SubElement(parent, 'mxCell')

        for key, value in cell_data.items():
            if key == 'geometry':
                # mxGeometry要素を作成
                geom = ET.SubElement(cell, 'mxGeometry')
                for g_key, g_value in value.items():
                    geom.set(g_key, str(g_value))
            else:
                # 属性として設定
                cell.set(key, str(value))

    @staticmethod
    def create_group_cell(cell_id: str, x: int, y: int, width: int, height: int,
                          parent: str = '1') -> Dict[str, Any]:
        """
        グループセルを生成（複数要素をまとめる親コンテナ）

        Args:
            cell_id: セルID
            x, y: 位置
            width, height: サイズ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        style = 'group;'

        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'vertex': '1',
            'connectable': '0',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_table_rect(cell_id: str, x: int, y: int, width: int, height: int,
                          bgcolor: str = '#ffffff', use_gradient: bool = False,
                          parent: str = '1') -> Dict[str, Any]:
        """
        テーブル外枠の矩形を生成

        Args:
            cell_id: セルID
            x, y: 位置
            width, height: サイズ
            bgcolor: 背景色
            use_gradient: グラデーション使用フラグ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        style = f'rounded=0;whiteSpace=wrap;html=1;fillColor={bgcolor};strokeColor=#000000;strokeWidth=2;'
        if use_gradient:
            style += 'gradientColor=#ffffff;gradientDirection=east;'

        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'vertex': '1',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_header_rect(cell_id: str, x: int, y: int, width: int, height: int,
                           bgcolor: str = '#ffffff', use_gradient: bool = False,
                           parent: str = '1') -> Dict[str, Any]:
        """
        ヘッダー背景の矩形を生成

        Args:
            cell_id: セルID
            x, y: 位置
            width, height: サイズ
            bgcolor: 背景色
            use_gradient: グラデーション使用フラグ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        style = f'rounded=0;whiteSpace=wrap;html=1;fillColor={bgcolor};strokeColor=#000000;strokeWidth=1;'
        if use_gradient:
            style += 'gradientColor=#ffffff;gradientDirection=east;'

        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'vertex': '1',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_text_cell(cell_id: str, value: str, x: int, y: int, width: int, height: int,
                         font_size: int = 10, font_weight: str = 'normal',
                         align: str = 'left', parent: str = '1') -> Dict[str, Any]:
        """
        テキストセルを生成

        Args:
            cell_id: セルID
            value: 表示テキスト
            x, y: 位置
            width, height: サイズ
            font_size: フォントサイズ
            font_weight: フォントウェイト (normal/bold)
            align: テキスト配置 (left/center/right)
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        font_style = '1' if font_weight == 'bold' else '0'
        style = (
            f'text;html=1;strokeColor=none;fillColor=none;align={align};'
            f'verticalAlign=middle;whiteSpace=wrap;rounded=0;'
            f'fontSize={font_size};fontStyle={font_style};'
        )

        return {
            'id': cell_id,
            'value': value,
            'style': style,
            'vertex': '1',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_marker_rect(cell_id: str, x: int, y: int, width: int, height: int,
                           parent: str = '1') -> Dict[str, Any]:
        """
        NOT NULLマーカー（黒四角）を生成

        Args:
            cell_id: セルID
            x, y: 位置
            width, height: サイズ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        style = 'rounded=0;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=none;'

        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'vertex': '1',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_line(cell_id: str, x1: int, y1: int, x2: int, y2: int,
                    stroke_width: int = 1, parent: str = '1') -> Dict[str, Any]:
        """
        線を生成

        Args:
            cell_id: セルID
            x1, y1: 開始位置
            x2, y2: 終了位置
            stroke_width: 線の太さ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        # 線の長さと位置を計算
        width = abs(x2 - x1) if x2 != x1 else 1
        height = abs(y2 - y1) if y2 != y1 else 1
        x = min(x1, x2)
        y = min(y1, y2)

        if x2 == x1:
            # 縦線
            style = f'endArrow=none;html=1;strokeWidth={stroke_width};'
        else:
            # 横線
            style = f'endArrow=none;html=1;strokeWidth={stroke_width};'

        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'edge': '1',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'relative': '1',
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_horizontal_line(cell_id: str, x: int, y: int, width: int,
                               stroke_width: int = 1, parent: str = '1') -> Dict[str, Any]:
        """
        水平線を生成（shape=lineを使用）

        Args:
            cell_id: セルID
            x, y: 開始位置
            width: 線の長さ
            stroke_width: 線の太さ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        style = f'line;strokeWidth={stroke_width};fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;strokeColor=#000000;'

        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'vertex': '1',
            'connectable': '0',
            'parent': parent,
            'geometry': {
                'x': x,
                'y': y,
                'width': width,
                'height': 1,
                'as': 'geometry'
            }
        }

    @staticmethod
    def create_edge_cell(cell_id: str, from_cell_id: str, to_cell_id: str, style: str, parent: str = '1') -> Dict[str, Any]:
        """
        エッジ（関係線）用のmxCellデータを生成

        Args:
            cell_id: セルID
            from_cell_id: 開始ノードのセルID
            to_cell_id: 終了ノードのセルID
            style: エッジのスタイル文字列
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        return {
            'id': cell_id,
            'value': '',
            'style': style,
            'edge': '1',
            'parent': parent,
            'source': from_cell_id,
            'target': to_cell_id,
            'geometry': {
                'relative': '1',
                'as': 'geometry'
            }
        }
