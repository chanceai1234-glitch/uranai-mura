"""
四柱推命占いの使用例

このファイルは四柱推命占いの基本的な使用方法を示すサンプルです。
"""
from datetime import datetime
from .base import DivinationInput
from .shichusuimei import ShichusuimeiDivination


def main():
    """四柱推命占いの実行例"""
    
    # 占いインスタンスの作成
    divination = ShichusuimeiDivination()
    
    # 入力データの作成（例：1990年5月15日 10時30分生まれ）
    input_data = DivinationInput(
        birth_date=datetime(1990, 5, 15, 10, 30),
        name="田中太郎",
        gender="男性"
    )
    
    try:
        # 占い実行
        result = divination.divinate(input_data)
        
        # 結果表示
        print("=" * 50)
        print(f"【{result.fortune_type}】占い結果")
        print("=" * 50)
        print(f"対象者: {input_data.name}")
        print(f"生年月日: {input_data.birth_date.strftime('%Y年%m月%d日 %H時%M分')}")
        print()
        
        print(f"総合運勢スコア: {result.overall_score}/100")
        print(f"総合結果: {result.summary}")
        print()
        
        # 四柱表示
        print("【四柱】")
        shicchu = result.detailed_results["四柱"]
        print(f"年柱: {shicchu['年柱']}  月柱: {shicchu['月柱']}")
        print(f"日柱: {shicchu['日柱']}  時柱: {shicchu['時柱']}")
        print()
        
        # 五行バランス
        print("【五行バランス】")
        balance = result.detailed_results["五行バランス"]
        for element, count in balance.items():
            bar = "■" * count + "□" * (10 - count)
            print(f"{element}: {bar} ({count})")
        print()
        
        print(f"日干（本命）: {result.detailed_results['日干']} ({result.detailed_results['本命']})")
        print()
        
        # アドバイス
        if result.advice:
            print("【アドバイス】")
            for i, advice in enumerate(result.advice, 1):
                print(f"{i}. {advice}")
            print()
        
        # ラッキーアイテム
        if result.lucky_items:
            print("【ラッキーアイテム】")
            print(", ".join(result.lucky_items))
        
        print("=" * 50)
        
    except ValueError as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()