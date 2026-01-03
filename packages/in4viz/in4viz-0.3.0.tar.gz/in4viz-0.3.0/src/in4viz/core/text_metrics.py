"""文字幅計算のための共通ユーティリティ"""


def calculate_text_width(text: str, is_japanese: bool = True) -> int:
    """
    テキストの幅を計算（日本語/英語を区別）

    Args:
        text: 計算対象のテキスト
        is_japanese: True なら日本語として計算、False なら英語として計算

    Returns:
        計算されたテキスト幅（ピクセル）
    """
    if is_japanese:
        return len(text) * 11
    else:
        return len(text) * 6
