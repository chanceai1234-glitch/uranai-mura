"""
占いモジュールの共通インターフェース
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DivinationInput:
    """占い入力データの共通クラス"""
    birth_date: datetime
    name: Optional[str] = None
    gender: Optional[str] = None  # "男性" or "女性"
    birth_place: Optional[str] = None


@dataclass
class DivinationResult:
    """占い結果の共通クラス"""
    fortune_type: str  # 占いの種類
    overall_score: int  # 総合運勢スコア (0-100)
    summary: str  # 総合結果の要約
    detailed_results: Dict[str, Any]  # 詳細結果
    advice: List[str]  # アドバイス
    lucky_items: List[str]  # ラッキーアイテム
    created_at: datetime


class DivinationBase(ABC):
    """占いモジュールの基底クラス"""
    
    @property
    @abstractmethod
    def fortune_type(self) -> str:
        """占いの種類を返す"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: DivinationInput) -> bool:
        """入力データのバリデーション"""
        pass
    
    @abstractmethod
    def calculate(self, input_data: DivinationInput) -> DivinationResult:
        """占い計算の実行"""
        pass
    
    def divinate(self, input_data: DivinationInput) -> DivinationResult:
        """占い実行のエントリーポイント"""
        if not self.validate_input(input_data):
            raise ValueError("入力データが無効です")
        
        return self.calculate(input_data)