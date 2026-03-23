"""
四柱推命モジュール

生年月日から四柱（年柱、月柱、日柱、時柱）を算出し、
五行の相関関係から運勢を占う。
"""
from typing import Dict, List, Tuple, Any
from datetime import datetime, date
from dataclasses import dataclass
import calendar

from .base import DivinationBase, DivinationInput, DivinationResult


# 四柱推命の基礎データ
JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]  # 十干
JUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]  # 十二支

# 五行対応表
GOGYOU_JIKKAN = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

GOGYOU_JUNISHI = {
    "寅": "木", "卯": "木", "巳": "火", "午": "火", "辰": "土", "戌": "土",
    "未": "土", "丑": "土", "申": "金", "酉": "金", "亥": "水", "子": "水"
}

# 五行相生・相克関係
SOUSHOU = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # 相生
SOUKOKU = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}  # 相克


@dataclass
class Hashira:
    """四柱の柱を表すクラス"""
    jikkan: str  # 十干
    junishi: str  # 十二支
    gogyou_jikkan: str  # 十干の五行
    gogyou_junishi: str  # 十二支の五行


@dataclass
class Shichusuimei:
    """四柱推命の計算結果"""
    nen_hashira: Hashira  # 年柱
    getsu_hashira: Hashira  # 月柱
    nichi_hashira: Hashira  # 日柱
    ji_hashira: Hashira  # 時柱
    gogyou_balance: Dict[str, int]  # 五行バランス


class ShichusuimeiDivination(DivinationBase):
    """四柱推命占いクラス"""
    
    @property
    def fortune_type(self) -> str:
        return "四柱推命"
    
    def validate_input(self, input_data: DivinationInput) -> bool:
        """入力データのバリデーション"""
        if not isinstance(input_data.birth_date, datetime):
            return False
        
        # 生年月日の妥当性チェック
        birth_year = input_data.birth_date.year
        if birth_year < 1900 or birth_year > datetime.now().year:
            return False
        
        return True
    
    def _calculate_rokuju_kanshi(self, year: int, month: int, day: int, hour: int = 0) -> Tuple[str, str]:
        """六十干支を計算する"""
        # 簡易的な計算（実際はもっと複雑な暦計算が必要）
        base_year = 1984  # 甲子年
        year_diff = year - base_year
        jikkan_index = year_diff % 10
        junishi_index = year_diff % 12
        
        return JIKKAN[jikkan_index], JUNISHI[junishi_index]
    
    def _calculate_nen_hashira(self, birth_date: datetime) -> Hashira:
        """年柱を計算"""
        jikkan, junishi = self._calculate_rokuju_kanshi(birth_date.year, 1, 1)
        return Hashira(
            jikkan=jikkan,
            junishi=junishi,
            gogyou_jikkan=GOGYOU_JIKKAN[jikkan],
            gogyou_junishi=GOGYOU_JUNISHI[junishi]
        )
    
    def _calculate_getsu_hashira(self, birth_date: datetime) -> Hashira:
        """月柱を計算"""
        # 月の十干支計算（簡易版）
        month_offset = birth_date.month - 1
        jikkan_index = (birth_date.year % 10 * 2 + month_offset) % 10
        junishi_index = (month_offset + 2) % 12  # 寅月から始まる
        
        jikkan = JIKKAN[jikkan_index]
        junishi = JUNISHI[junishi_index]
        
        return Hashira(
            jikkan=jikkan,
            junishi=junishi,
            gogyou_jikkan=GOGYOU_JIKKAN[jikkan],
            gogyou_junishi=GOGYOU_JUNISHI[junishi]
        )
    
    def _calculate_nichi_hashira(self, birth_date: datetime) -> Hashira:
        """日柱を計算"""
        # 日の十干支計算（簡易版）
        days_since_base = (birth_date.date() - date(1900, 1, 1)).days
        jikkan_index = days_since_base % 10
        junishi_index = days_since_base % 12
        
        jikkan = JIKKAN[jikkan_index]
        junishi = JUNISHI[junishi_index]
        
        return Hashira(
            jikkan=jikkan,
            junishi=junishi,
            gogyou_jikkan=GOGYOU_JIKKAN[jikkan],
            gogyou_junishi=GOGYOU_JUNISHI[junishi]
        )
    
    def _calculate_ji_hashira(self, birth_date: datetime) -> Hashira:
        """時柱を計算"""
        hour = birth_date.hour
        # 時刻を十二支に対応（子の刻：23-1時）
        junishi_index = ((hour + 1) // 2) % 12
        
        # 日干から時干を求める（簡易版）
        nichi_hashira = self._calculate_nichi_hashira(birth_date)
        nichi_jikkan_index = JIKKAN.index(nichi_hashira.jikkan)
        jikkan_index = (nichi_jikkan_index * 2 + junishi_index) % 10
        
        jikkan = JIKKAN[jikkan_index]
        junishi = JUNISHI[junishi_index]
        
        return Hashira(
            jikkan=jikkan,
            junishi=junishi,
            gogyou_jikkan=GOGYOU_JIKKAN[jikkan],
            gogyou_junishi=GOGYOU_JUNISHI[junishi]
        )
    
    def _calculate_gogyou_balance(self, shichusuimei: Shichusuimei) -> Dict[str, int]:
        """五行のバランスを計算"""
        balance = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        
        # 各柱の五行を集計
        for hashira in [shichusuimei.nen_hashira, shichusuimei.getsu_hashira, 
                       shichusuimei.nichi_hashira, shichusuimei.ji_hashira]:
            balance[hashira.gogyou_jikkan] += 2  # 十干は重み2
            balance[hashira.gogyou_junishi] += 1  # 十二支は重み1
        
        return balance
    
    def _analyze_fortune(self, shichusuimei: Shichusuimei) -> Tuple[int, str, List[str], List[str]]:
        """運勢分析"""
        balance = shichusuimei.gogyou_balance
        nichi_gogyou = shichusuimei.nichi_hashira.gogyou_jikkan  # 日干＝本人の五行
        
        # 基本スコア計算
        base_score = 50
        
        # 五行バランスによる調整
        max_element = max(balance.values())
        min_element = min(balance.values())
        balance_score = 100 - (max_element - min_element) * 10
        
        # 日干の強弱による調整
        nichi_strength = balance[nichi_gogyou]
        if nichi_strength >= 6:
            strength_modifier = 20  # 身強
        elif nichi_strength <= 2:
            strength_modifier = -10  # 身弱
        else:
            strength_modifier = 0  # 中和
        
        overall_score = max(0, min(100, base_score + balance_score//10 + strength_modifier))
        
        # 総合結果の生成
        if overall_score >= 80:
            summary = "非常に良好な運勢です。持って生まれた資質が十分に発揮されるでしょう。"
        elif overall_score >= 60:
            summary = "概ね良好な運勢です。努力により更なる向上が期待できます。"
        elif overall_score >= 40:
            summary = "平均的な運勢です。バランスの取れた生活を心がけましょう。"
        else:
            summary = "やや注意が必要な運勢です。慎重な行動を心がけてください。"
        
        # アドバイス生成
        advice = []
        dominant_element = max(balance, key=balance.get)
        weak_element = min(balance, key=balance.get)
        
        if balance[dominant_element] > balance[weak_element] + 3:
            advice.append(f"{dominant_element}の気が強すぎるため、{weak_element}の要素を生活に取り入れましょう。")
        
        if nichi_strength <= 2:
            advice.append("日干が弱いため、自信を持って行動することを心がけてください。")
        elif nichi_strength >= 6:
            advice.append("日干が強いため、謙虚さと協調性を大切にしてください。")
        
        # ラッキーアイテム
        lucky_items = self._get_lucky_items(nichi_gogyou, balance)
        
        return overall_score, summary, advice, lucky_items
    
    def _get_lucky_items(self, nichi_gogyou: str, balance: Dict[str, int]) -> List[str]:
        """ラッキーアイテムの生成"""
        weak_elements = [elem for elem, count in balance.items() if count < 3]
        
        lucky_map = {
            "木": ["観葉植物", "緑色のアイテム", "木製の小物"],
            "火": ["赤色のアイテム", "キャンドル", "暖色系のアクセサリー"],
            "土": ["陶器", "黄色いアイテム", "土や石のアクセサリー"],
            "金": ["金属製のアクセサリー", "白色のアイテム", "時計"],
            "水": ["青色のアイテム", "水晶", "鏡"]
        }
        
        lucky_items = []
        for element in weak_elements:
            lucky_items.extend(lucky_map.get(element, []))
        
        # 相生関係も考慮
        support_element = SOUSHOU.get(nichi_gogyou, "")
        if support_element and balance[support_element] < 4:
            lucky_items.extend(lucky_map.get(support_element, []))
        
        return list(set(lucky_items))[:5]  # 重複除去して最大5個
    
    def calculate(self, input_data: DivinationInput) -> DivinationResult:
        """四柱推命の計算実行"""
        birth_date = input_data.birth_date
        
        # 四柱の計算
        nen_hashira = self._calculate_nen_hashira(birth_date)
        getsu_hashira = self._calculate_getsu_hashira(birth_date)
        nichi_hashira = self._calculate_nichi_hashira(birth_date)
        ji_hashira = self._calculate_ji_hashira(birth_date)
        
        # 四柱推命オブジェクトの作成
        shichusuimei = Shichusuimei(
            nen_hashira=nen_hashira,
            getsu_hashira=getsu_hashira,
            nichi_hashira=nichi_hashira,
            ji_hashira=ji_hashira,
            gogyou_balance={}
        )
        
        # 五行バランス計算
        shichusuimei.gogyou_balance = self._calculate_gogyou_balance(shichusuimei)
        
        # 運勢分析
        overall_score, summary, advice, lucky_items = self._analyze_fortune(shichusuimei)
        
        # 詳細結果の構築
        detailed_results = {
            "四柱": {
                "年柱": f"{nen_hashira.jikkan}{nen_hashira.junishi}",
                "月柱": f"{getsu_hashira.jikkan}{getsu_hashira.junishi}",
                "日柱": f"{nichi_hashira.jikkan}{nichi_hashira.junishi}",
                "時柱": f"{ji_hashira.jikkan}{ji_hashira.junishi}"
            },
            "五行バランス": shichusuimei.gogyou_balance,
            "日干": nichi_hashira.jikkan,
            "本命": nichi_hashira.gogyou_jikkan
        }
        
        return DivinationResult(
            fortune_type=self.fortune_type,
            overall_score=overall_score,
            summary=summary,
            detailed_results=detailed_results,
            advice=advice,
            lucky_items=lucky_items,
            created_at=datetime.now()
        )