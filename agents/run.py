"""エージェント実行エントリーポイント

使い方:
    # 単一の占い手法を Phase 1 パイプラインで処理
    python -m agents.run phase1 四柱推命 --region East-Asia

    # 複数の占い手法をバッチ処理
    python -m agents.run phase1-batch --file targets.json

    # 個別エージェントを直接実行
    python -m agents.run researcher 四柱推命
    python -m agents.run scientist 四柱推命 10_Research/East-Asia/四柱推命.md
    python -m agents.run reviewer 10_Research/East-Asia/四柱推命.md research
"""

import argparse
import asyncio
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="占い村 エージェント実行")
    subparsers = parser.add_subparsers(dest="command", help="実行コマンド")

    # phase1: 単一占いの完全パイプライン
    p1 = subparsers.add_parser("phase1", help="Phase 1 パイプライン実行")
    p1.add_argument("uranai", help="占い名")
    p1.add_argument("--region", default="East-Asia", help="地域 (default: East-Asia)")

    # phase1-batch: 複数占いのバッチ処理
    p1b = subparsers.add_parser("phase1-batch", help="Phase 1 バッチ実行")
    p1b.add_argument("--file", required=True, help="対象リストのJSONファイル")
    p1b.add_argument("--concurrent", type=int, default=3, help="最大並列数")

    # 個別エージェント
    res = subparsers.add_parser("researcher", help="Researcher 単体実行")
    res.add_argument("uranai", help="占い名")

    sci = subparsers.add_parser("scientist", help="Scientist 単体実行")
    sci.add_argument("uranai", help="占い名")
    sci.add_argument("note_path", help="リサーチノートのパス")

    rev = subparsers.add_parser("reviewer", help="Research Reviewer 単体実行")
    rev.add_argument("note_path", help="レビュー対象ノートのパス")
    rev.add_argument("--type", default="research", choices=["research", "science", "article"])

    args = parser.parse_args()

    if args.command == "phase1":
        from agents.pipeline_phase1 import run_pipeline

        result = asyncio.run(run_pipeline(args.uranai, args.region))
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "phase1-batch":
        from agents.pipeline_phase1 import run_batch_pipeline

        with open(args.file, encoding="utf-8") as f:
            targets = json.load(f)
        results = asyncio.run(run_batch_pipeline(targets, args.concurrent))
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "researcher":
        from agents.researcher import run

        result = asyncio.run(run(args.uranai))
        print(result)

    elif args.command == "scientist":
        from agents.scientist import run

        result = asyncio.run(run(args.uranai, args.note_path))
        print(result)

    elif args.command == "reviewer":
        from agents.research_reviewer import run

        result = asyncio.run(run(args.note_path, args.type))
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
