"""
占いモジュール

各種占いロジックを提供するパッケージ
"""
from .base import DivinationBase, DivinationInput, DivinationResult
from .shichusuimei import ShichusuimeiDivination

__all__ = [
    "DivinationBase",
    "DivinationInput", 
    "DivinationResult",
    "ShichusuimeiDivination"
]

# 占い種類の登録
DIVINATION_TYPES = {
    "四柱推命": ShichusuimeiDivination,
}


def get_divination(divination_type: str) -> DivinationBase:
    """指定された占い種類のインスタンスを取得する
    
    Args:
        divination_type: 占いの種類
        
    Returns:
        占いクラスのインスタンス
        
    Raises:
        ValueError: 指定された占い種類が存在しない場合
    """
    if divination_type not in DIVINATION_TYPES:
        available_types = ", ".join(DIVINATION_TYPES.keys())
        raise ValueError(f"占い種類 '{divination_type}' は存在しません。利用可能な種類: {available_types}")
    
    return DIVINATION_TYPES[divination_type]()