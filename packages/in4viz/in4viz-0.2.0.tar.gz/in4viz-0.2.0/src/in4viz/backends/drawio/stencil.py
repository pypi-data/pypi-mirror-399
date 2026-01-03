from typing import List, Dict, Any
from ...core.text_metrics import calculate_text_width
from .generator import DrawioGenerator


class DrawioTableStencil:
    """draw.io用のテーブルステンシル（swimlane形式）"""

    def __init__(self, width: int = 400, min_height: int = 100):
        self.width = width
        self.min_height = min_height
        self.row_height = 22
        self.header_height = 26
        self.min_logical_width = 40
        self.min_marker_width = 6
        self.min_physical_width = 30
        self.min_data_type_width = 45
        self.min_constraint_width = 25
        self.padding = 10

    def _calculate_widths(self, data: Dict[str, Any]) -> Dict[str, int]:
        """テーブルとカラムの幅を計算"""
        physical_name = data.get('table_name', 'Table')
        logical_name = data.get('logical_name', physical_name)
        columns = data.get('columns', [])

        # テーブル名の幅計算
        logical_table_width = max(self.min_logical_width, calculate_text_width(logical_name, True) + self.padding)
        physical_table_width = max(self.min_physical_width, calculate_text_width(physical_name, False) + self.padding)
        table_total_width = logical_table_width + physical_table_width

        # カラム名の幅計算
        max_logical_col_width = self.min_logical_width
        marker_width = self.min_marker_width
        max_physical_col_width = self.min_physical_width
        max_type_width = self.min_data_type_width
        max_constraint_width = self.min_constraint_width

        for column in columns:
            physical_col_name = column.get('name', '')
            logical_col_name = column.get('logical_name', physical_col_name)
            column_type = column.get('type', 'VARCHAR')

            # 制約文字列の計算
            constraints = []
            if column.get('foreign_key', False):
                constraints.append('FK')
            if column.get('index', False):
                constraints.append('IDX')
            constraint_text = ', '.join(constraints) if constraints else ''

            max_logical_col_width = max(max_logical_col_width, calculate_text_width(logical_col_name, True) + self.padding)
            max_physical_col_width = max(max_physical_col_width, calculate_text_width(physical_col_name, False) + self.padding)
            max_type_width = max(max_type_width, calculate_text_width(column_type, False) + self.padding)
            if constraint_text:
                max_constraint_width = max(max_constraint_width, calculate_text_width(constraint_text, False) + self.padding)

        # 制約欄に内容がない場合は幅0
        if max_constraint_width == self.min_constraint_width:
            has_constraints = any(column.get('foreign_key', False) or column.get('index', False) for column in columns)
            if not has_constraints:
                max_constraint_width = 0

        column_total_width = marker_width + max_logical_col_width + max_physical_col_width + max_type_width + max_constraint_width

        return {
            'table_logical_width': logical_table_width,
            'table_physical_width': physical_table_width,
            'table_total_width': table_total_width,
            'logical_width': max_logical_col_width,
            'marker_width': marker_width,
            'physical_width': max_physical_col_width,
            'type_width': max_type_width,
            'constraint_width': max_constraint_width,
            'column_total_width': column_total_width,
            'total_width': max(table_total_width, column_total_width)
        }

    def calculate_height(self, data: Dict[str, Any]) -> int:
        """テーブルの高さを計算"""
        columns = data.get('columns', [])
        pk_columns = [col for col in columns if col.get('primary_key', False)]
        regular_columns = [col for col in columns if not col.get('primary_key', False)]

        # PKのみのテーブルの場合、空行を1行追加
        extra_rows = 1 if len(pk_columns) > 0 and len(regular_columns) == 0 else 0
        return self.header_height + (len(columns) + extra_rows) * self.row_height

    def get_width(self, data: Dict[str, Any]) -> int:
        """テーブルの幅を取得"""
        widths = self._calculate_widths(data)
        return widths['total_width']

    def render_mxcells(self, data: Dict[str, Any], x: int, y: int, canvas):
        """
        draw.io用のmxCellリストを生成

        Args:
            data: テーブルデータ
            x, y: 位置
            canvas: DrawioCanvasインスタンス（セルID生成用）

        Returns:
            (mxCellデータのリスト, テーブルセルID)
        """
        cells = []
        physical_name = data.get('table_name', 'Table')
        logical_name = data.get('logical_name', physical_name)
        columns = data.get('columns', [])

        # PKカラムと通常カラムを分離
        pk_columns = [col for col in columns if col.get('primary_key', False)]
        regular_columns = [col for col in columns if not col.get('primary_key', False)]
        sorted_columns = pk_columns + regular_columns

        # 幅・高さ計算
        widths = self._calculate_widths(data)
        width = widths['total_width']
        height = self.calculate_height(data)

        # テーブル名表示（論理名 (物理名) 形式）
        table_display = f'{logical_name} ({physical_name})' if logical_name != physical_name else logical_name

        # 親テーブルセル（swimlane）を作成
        table_cell_id = canvas.get_next_cell_id()
        table_cell = DrawioGenerator.create_table_cell(
            cell_id=table_cell_id,
            value=table_display,
            x=x,
            y=y,
            width=width,
            height=height
        )
        cells.append(table_cell)

        # カラムセルを作成
        y_offset = self.header_height
        for i, column in enumerate(sorted_columns):
            physical_col_name = column.get('name', f'Column{i}')
            logical_col_name = column.get('logical_name', physical_col_name)
            column_type = column.get('type', 'VARCHAR')
            is_primary = column.get('primary_key', False)
            is_nullable = column.get('nullable', True)
            is_foreign_key = column.get('foreign_key', False)

            # 制約文字列
            constraints = []
            if is_foreign_key:
                constraints.append('FK')
            if column.get('index', False):
                constraints.append('IDX')
            constraint_text = ', '.join(constraints) if constraints else ''

            # カラム表示テキスト
            # NOT NULLマーカー（黒四角）を先頭に追加
            marker = '■ ' if not is_nullable else ''
            # フォーマット: ■ 論理名 (物理名) 型 [制約]
            column_display = f'{marker}{logical_col_name} ({physical_col_name}) {column_type}'
            if constraint_text:
                column_display += f' [{constraint_text}]'
            if is_primary:
                column_display += ' [PK]'

            # 最後のPKカラムかどうか
            is_last_pk = is_primary and i == len(pk_columns) - 1 and len(regular_columns) > 0

            column_cell_id = canvas.get_next_cell_id()
            column_cell = DrawioGenerator.create_column_cell(
                cell_id=column_cell_id,
                value=column_display,
                y_offset=y_offset,
                width=width,
                parent_id=table_cell_id,
                is_last_pk=is_last_pk
            )
            cells.append(column_cell)

            y_offset += self.row_height

        # PKのみのテーブルの場合、空行を追加
        if len(pk_columns) > 0 and len(regular_columns) == 0:
            empty_cell_id = canvas.get_next_cell_id()
            empty_cell = DrawioGenerator.create_column_cell(
                cell_id=empty_cell_id,
                value='',
                y_offset=y_offset,
                width=width,
                parent_id=table_cell_id,
                is_last_pk=False
            )
            cells.append(empty_cell)

        return cells, table_cell_id
