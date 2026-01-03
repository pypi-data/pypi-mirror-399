# in4viz - ER図可視化ライブラリ

Python製のER図専用可視化ライブラリ。SVGとdraw.io形式での出力をサポートします。

## 特徴

- **2つの出力形式**: SVGとdraw.io (mxGraph XML)
- **統合されたコアアーキテクチャ**: 共通のデータモデルとレイアウトエンジン
- **自動レイアウト**: FK関係を考慮した階層的配置
- **日本語対応**: 論理名・物理名の両方表示
- **カーディナリティ表示**: IE記法でのカーディナリティ表現
- **複数の線種**: 直線、クランク、スプライン

## インストール

```bash
pip install in4viz
```

## 基本的な使い方

### SVG出力

```python
from in4viz import ERDiagram, Table, Column, LineType, Cardinality

# SVGバックエンドでER図を作成
diagram = ERDiagram(backend='svg')

# テーブルを定義
users_table = Table(
    name='users',
    logical_name='ユーザー',
    columns=[
        Column('id', 'ID', 'INT', primary_key=True, nullable=False),
        Column('name', '名前', 'VARCHAR(100)', nullable=False),
        Column('email', 'メール', 'VARCHAR(255)', nullable=False, index=True),
    ]
)

posts_table = Table(
    name='posts',
    logical_name='投稿',
    columns=[
        Column('id', 'ID', 'INT', primary_key=True, nullable=False),
        Column('user_id', 'ユーザーID', 'INT', nullable=False, foreign_key=True),
        Column('title', 'タイトル', 'VARCHAR(200)', nullable=False),
        Column('content', '本文', 'TEXT'),
    ]
)

# テーブルを追加
diagram.add_table(users_table)
diagram.add_table(posts_table)

# FK関係を追加
diagram.add_edge(
    'posts', 'users',
    line_type=LineType.CRANK,
    cardinality=Cardinality(from_side='*', to_side='1')
)

# SVGファイルとして保存
diagram.save('er_diagram.svg')
```

### draw.io出力

```python
from in4viz import ERDiagram, Table, Column

# draw.ioバックエンドでER図を作成
diagram = ERDiagram(backend='drawio')

# テーブルを追加（同じTableオブジェクトを使用）
diagram.add_table(users_table)
diagram.add_table(posts_table)
diagram.add_edge('posts', 'users')

# draw.ioファイルとして保存
diagram.save('er_diagram.drawio')
```

### バックエンド直接指定

特定のバックエンドを直接使用することもできます：

```python
from in4viz.backends.svg import SVGERDiagram
from in4viz.backends.drawio import DrawioERDiagram

# SVG専用
svg_diagram = SVGERDiagram()
svg_diagram.add_table(users_table)
svg_diagram.save_svg('output.svg')

# draw.io専用
drawio_diagram = DrawioERDiagram()
drawio_diagram.add_table(users_table)
drawio_diagram.save_drawio('output.drawio')
```

## アーキテクチャ

```
in4viz/
├── core/                  # 共通コア（80%）
│   ├── models.py         # データモデル（Table, Column, LineType, Cardinality）
│   ├── layout.py         # レイアウトアルゴリズム（階層構築、自動配置）
│   └── text_metrics.py   # 文字幅計算
├── backends/             # 出力形式別実装（20%）
│   ├── svg/             # SVG出力
│   │   ├── canvas.py
│   │   ├── stencil.py
│   │   └── renderer.py
│   └── drawio/          # draw.io出力
│       ├── canvas.py
│       ├── stencil.py
│       ├── renderer.py
│       └── generator.py
└── er_diagram.py        # ユーザーAPI
```

## 主要機能

### データモデル

- `Table`: テーブル定義（論理名・物理名）
- `Column`: カラム定義（型、制約、PK/FK/Index）
- `LineType`: 線種（STRAIGHT, CRANK, SPLINE）
- `Cardinality`: カーディナリティ（1, 0..1, *, 1..*など）

### レイアウトエンジン

- FK関係を考慮した階層的自動配置
- 逆トポロジカルソートによる階層構築
- 関連テーブルの隣接配置
- 動的キャンバスサイズ調整

### 表示機能

- テーブル名：論理名 (物理名)
- カラム：論理名 (物理名) 型 [制約]
- PKカラムの境界線表示
- NOT NULLマーカー（黒四角）
- FK、Indexの制約表示

## ライセンス

MIT License

## 開発

```bash
# 開発モードでインストール
cd packages/in4viz
pip install -e .

# テスト実行
pytest
```

## 貢献

プルリクエストを歓迎します！バグ報告や機能要望はIssueでお願いします。
