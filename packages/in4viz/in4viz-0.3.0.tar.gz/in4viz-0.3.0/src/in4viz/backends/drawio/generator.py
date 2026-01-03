import xml.etree.ElementTree as ET
from typing import List, Dict, Any


class DrawioGenerator:
    """draw.io (mxGraph) XML生成ユーティリティ"""

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
    def create_table_cell(cell_id: str, value: str, x: int, y: int, width: int, height: int, parent: str = '1') -> Dict[str, Any]:
        """
        テーブル用のswimlane mxCellデータを生成

        Args:
            cell_id: セルID
            value: テーブル名（表示テキスト）
            x, y: 位置
            width, height: サイズ
            parent: 親セルID

        Returns:
            mxCellデータ辞書
        """
        style = (
            'swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;'
            'startSize=26;fillColor=#e1d5e7;horizontalStack=0;'
            'resizeParent=1;resizeParentMax=0;resizeLast=0;'
            'collapsible=0;marginBottom=0;swimlaneFillColor=#ffffff;'
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
    def create_column_cell(cell_id: str, value: str, y_offset: int, width: int, parent_id: str, is_last_pk: bool = False) -> Dict[str, Any]:
        """
        カラム用のtext mxCellデータを生成

        Args:
            cell_id: セルID
            value: カラム情報（表示テキスト）
            y_offset: 親からのY座標オフセット
            width: 幅
            parent_id: 親テーブルのセルID
            is_last_pk: 最後のPKカラムかどうか（境界線表示用）

        Returns:
            mxCellデータ辞書
        """
        base_style = (
            'text;strokeColor=none;fillColor=none;align=left;'
            'verticalAlign=top;spacingLeft=4;spacingRight=4;'
            'overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];'
            'portConstraint=eastwest;'
        )

        # 最後のPKカラムには境界線を追加
        if is_last_pk:
            base_style += 'strokeColor=#000000;strokeWidth=1;'

        return {
            'id': cell_id,
            'value': value,
            'style': base_style,
            'vertex': '1',
            'parent': parent_id,
            'geometry': {
                'y': y_offset,
                'width': width,
                'height': 26,
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
