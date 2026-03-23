# 占い村（uranai-mura）

## プロジェクト概要

占いの科学的検証・啓発プラットフォーム構築プロジェクト。
世界中の占い手法を体系的に収集・分類し、科学的根拠に基づいて検証する。

## ミッション

1. 世界中の占い手法を網羅的に収集・分類する
2. 各手法の効果を科学的に検証する
3. 検証結果を啓発コンテンツとして発信する
4. 占いを体験できるプラットフォームを構築し、ユーザーが自ら気づきを得られるようにする

## フェーズ構成

- **Phase 1**: 調査・分析（占い手法の収集、科学的検証）
- **Phase 2**: コンテンツ発信（啓発記事の作成・公開）
- **Phase 3**: 体験プラットフォーム構築（Webサービス開発）

## リポジトリ構造

```
uranai-mura/
├── agents/          ← Agent SDK エージェントコード
│   ├── tools/       ← 共通ツール（Obsidian連携、GitHub連携）
│   └── prompts/     ← 各エージェントのシステムプロンプト
├── research/        ← 既存リサーチデータ
├── src/             ← 体験プラットフォームコード（Phase 3）
├── content/         ← 公開用コンテンツ（Phase 2）
└── tests/           ← テストコード
```

## エージェントチーム（10体）

| # | エージェント | ファイル | 役割 |
|---|------------|---------|------|
| 1 | Researcher | agents/researcher.py | 占い手法の収集・分類 |
| 2 | Scientist | agents/scientist.py | 科学的検証 |
| 3 | Research Reviewer | agents/research_reviewer.py | リサーチ品質チェック |
| 4 | Writer | agents/writer.py | 啓発コンテンツ作成 |
| 5 | Requirements Analyst | agents/requirements_analyst.py | 要件定義 |
| 6 | Architect | agents/architect.py | システム設計 |
| 7 | Implementer | agents/implementer.py | コード実装 |
| 8 | Tester | agents/tester.py | テスト設計・実行 |
| 9 | Code Reviewer | agents/code_reviewer.py | コード品質検証 |
| 10 | Orchestrator | agents/orchestrator.py | 全体統括 |

## 外部連携

- **Obsidian Vault**: `C:\Users\加藤敦也KatoAtsuya\uranai-mura-vault`
  - ナレッジベース（リサーチ、検証結果、設計メモ）
- **GitHub**: このリポジトリ
  - コード管理、Issue/PRによるタスク管理

## 技術スタック

- **言語**: Python 3.12+
- **エージェント**: Anthropic Agent SDK
- **ナレッジ管理**: Obsidian（Markdownファイル直接操作）

## 開発ルール

- 科学的誠実さを最優先する。検証結果が「効果あり」なら正確に伝える
- 宗教・文化的な配慮を忘れない
- 生体情報（手相の写真等）は同意・用途限定・差別リスクに配慮
- 各エージェントの入出力フォーマットはテンプレートに従う
