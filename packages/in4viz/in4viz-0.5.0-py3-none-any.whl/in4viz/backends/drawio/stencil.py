from typing import List, Dict, Any, Tuple
from ...core.text_metrics import calculate_text_width
from .generator import DrawioGenerator


class DrawioTableStencil:
    """draw.io用のテーブルステンシル（テーブル形式 - SVGと同一レイアウト）"""

    def __init__(self, width: int = 400, min_height: int = 100):
        self.width = width
        self.min_height = min_height
        self.row_height = 22
        self.header_height = 25
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

    def render_mxcells(self, data: Dict[str, Any], x: int, y: int, canvas) -> Tuple[List[Dict[str, Any]], str]:
        """
        draw.io用のmxCellリストを生成（SVGと同一レイアウト、グループ化対応）

        Args:
            data: テーブルデータ
            x, y: 位置
            canvas: DrawioCanvasインスタンス（セルID生成用）

        Returns:
            (mxCellデータのリスト, グループセルID)
        """
        cells = []
        physical_name = data.get('table_name', 'Table')
        logical_name = data.get('logical_name', physical_name)
        columns = data.get('columns', [])
        bgcolor = data.get('bgcolor', '#ffffff')
        use_gradient = data.get('use_gradient', False)

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

        # 0. グループセルを作成（全要素の親）
        group_id = canvas.get_next_cell_id()
        group_cell = DrawioGenerator.create_group_cell(
            cell_id=group_id,
            x=x,
            y=y,
            width=width,
            height=height
        )
        cells.append(group_cell)

        # 以降の要素はグループ内の相対座標を使用
        # 1. テーブル外枠の矩形を作成
        table_rect_id = canvas.get_next_cell_id()
        table_rect = DrawioGenerator.create_table_rect(
            cell_id=table_rect_id,
            x=0,
            y=0,
            width=width,
            height=height,
            bgcolor=bgcolor,
            use_gradient=use_gradient,
            parent=group_id
        )
        cells.append(table_rect)

        # 2. ヘッダー背景の矩形を作成
        header_rect_id = canvas.get_next_cell_id()
        header_rect = DrawioGenerator.create_header_rect(
            cell_id=header_rect_id,
            x=0,
            y=0,
            width=width,
            height=self.header_height,
            bgcolor=bgcolor,
            use_gradient=use_gradient,
            parent=group_id
        )
        cells.append(header_rect)

        # 3. テーブル名テキストを作成
        header_text_id = canvas.get_next_cell_id()
        header_text = DrawioGenerator.create_text_cell(
            cell_id=header_text_id,
            value=table_display,
            x=5,
            y=0,
            width=width - 10,
            height=self.header_height,
            font_size=12,
            font_weight='bold',
            align='left',
            parent=group_id
        )
        cells.append(header_text)

        # 4. カラム行を作成
        current_y = self.header_height
        pk_end_y = None

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

            # セル位置計算（グループ内の相対座標）
            marker_col_x = 0
            logical_col_x = widths['marker_width']
            physical_col_x = widths['marker_width'] + widths['logical_width']
            type_col_x = widths['marker_width'] + widths['logical_width'] + widths['physical_width']
            constraint_col_x = widths['marker_width'] + widths['logical_width'] + widths['physical_width'] + widths['type_width']

            # NOT NULLマーカー表示
            if not is_nullable:
                marker_id = canvas.get_next_cell_id()
                marker_x = marker_col_x + 3
                marker_y = current_y + self.row_height // 2 - 3
                marker_cell = DrawioGenerator.create_marker_rect(
                    cell_id=marker_id,
                    x=marker_x,
                    y=marker_y,
                    width=3,
                    height=6,
                    parent=group_id
                )
                cells.append(marker_cell)

            # 論理名テキスト
            logical_text_id = canvas.get_next_cell_id()
            logical_text = DrawioGenerator.create_text_cell(
                cell_id=logical_text_id,
                value=logical_col_name,
                x=logical_col_x + 5,
                y=current_y,
                width=widths['logical_width'] - 5,
                height=self.row_height,
                font_size=10,
                font_weight='normal',
                align='left',
                parent=group_id
            )
            cells.append(logical_text)

            # 物理名テキスト
            physical_text_id = canvas.get_next_cell_id()
            physical_text = DrawioGenerator.create_text_cell(
                cell_id=physical_text_id,
                value=physical_col_name,
                x=physical_col_x + 5,
                y=current_y,
                width=widths['physical_width'] - 5,
                height=self.row_height,
                font_size=10,
                font_weight='normal',
                align='left',
                parent=group_id
            )
            cells.append(physical_text)

            # データ型テキスト
            type_text_id = canvas.get_next_cell_id()
            type_text = DrawioGenerator.create_text_cell(
                cell_id=type_text_id,
                value=column_type,
                x=type_col_x + 5,
                y=current_y,
                width=widths['type_width'] - 5,
                height=self.row_height,
                font_size=9,
                font_weight='normal',
                align='left',
                parent=group_id
            )
            cells.append(type_text)

            # 制約テキスト（制約欄がある場合のみ）
            if widths['constraint_width'] > 0:
                constraint_text_id = canvas.get_next_cell_id()
                constraint_cell = DrawioGenerator.create_text_cell(
                    cell_id=constraint_text_id,
                    value=constraint_text,
                    x=constraint_col_x + 5,
                    y=current_y,
                    width=widths['constraint_width'] - 5,
                    height=self.row_height,
                    font_size=9,
                    font_weight='normal',
                    align='left',
                    parent=group_id
                )
                cells.append(constraint_cell)

            current_y += self.row_height

            if is_primary:
                pk_end_y = current_y

        # 5. PK区切り線を作成（PKカラムがある場合）- テーブル幅全体に
        if pk_columns and pk_end_y and regular_columns:
            pk_line_id = canvas.get_next_cell_id()
            pk_line = DrawioGenerator.create_horizontal_line(
                cell_id=pk_line_id,
                x=0,
                y=pk_end_y,
                width=width,  # total_widthを使用
                stroke_width=1,
                parent=group_id
            )
            cells.append(pk_line)

        # グループセルIDを返す（エッジ接続用）
        return cells, group_id
