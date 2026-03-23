"""エージェント実行エントリーポイント

使い方:
    # Phase 1 パイプライン
    python -m agents.run phase1 四柱推命 --region East-Asia

    # 個別エージェント
    python -m agents.run researcher 四柱推命
    python -m agents.run scientist 四柱推命 10_Research/East-Asia/四柱推命.md
    python -m agents.run reviewer 10_Research/East-Asia/四柱推命.md --type research
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="占い村 エージェント実行")
    subparsers = parser.add_subparsers(dest="command", help="実行コマンド")

    # phase1
    p1 = subparsers.add_parser("phase1", help="Phase 1 パイプライン実行")
    p1.add_argument("uranai", help="占い名")
    p1.add_argument("--region", default="East-Asia", help="地域 (default: East-Asia)")

    # phase2: Phase 1 + Writer
    p2 = subparsers.add_parser("phase2", help="Phase 1 + Writer パイプライン実行")
    p2.add_argument("uranai", help="占い名")
    p2.add_argument("--region", default="East-Asia", help="地域 (default: East-Asia)")

    # 個別エージェント
    res = subparsers.add_parser("researcher", help="Researcher 単体実行")
    res.add_argument("uranai", help="占い名")

    sci = subparsers.add_parser("scientist", help="Scientist 単体実行")
    sci.add_argument("uranai", help="占い名")
    sci.add_argument("note_path", help="リサーチノートのパス")

    rev = subparsers.add_parser("reviewer", help="Research Reviewer 単体実行")
    rev.add_argument("note_path", help="レビュー対象ノートのパス")
    rev.add_argument("--type", default="research", choices=["research", "science", "article"])

    wrt = subparsers.add_parser("writer", help="Writer 単体実行")
    wrt.add_argument("uranai", help="占い名")
    wrt.add_argument("--science", default="", help="科学検証ノートのパス")
    wrt.add_argument("--research", default="", help="リサーチノートのパス")

    args = parser.parse_args()

    if args.command == "phase1":
        from agents.pipeline_phase1 import run_pipeline

        result = run_pipeline(args.uranai, args.region)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "phase2":
        from agents.pipeline_phase1 import run_pipeline
        from agents.writer import run as run_writer
        from agents.research_reviewer import run as run_review

        result = run_pipeline(args.uranai, args.region)
        if result["status"] == "completed":
            print(f"\n[4/5] Writer: 啓発記事を作成中...")
            run_writer(args.uranai, result["science_note"], result["research_note"])
            draft_path = f"30_Content/Drafts/{args.uranai}.md"
            print(f"  → 記事ドラフト作成完了: {draft_path}")

            print(f"\n[5/5] Research Reviewer: 記事レビュー中...")
            review = run_review(draft_path, "article")
            print(f"  → 記事レビュー: {'承認' if review['approved'] else '差し戻し'}")
            result["article_draft"] = draft_path
            result["article_review"] = review
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "researcher":
        from agents.researcher import run

        print(run(args.uranai))

    elif args.command == "scientist":
        from agents.scientist import run

        print(run(args.uranai, args.note_path))

    elif args.command == "reviewer":
        from agents.research_reviewer import run

        result = run(args.note_path, args.type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "writer":
        from agents.writer import run

        science = args.science or f"20_Science/Verdicts/{args.uranai}.md"
        research = args.research or ""
        print(run(args.uranai, science, research))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
