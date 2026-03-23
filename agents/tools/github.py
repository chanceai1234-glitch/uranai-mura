"""GitHub API ツール

エージェントがGitHub Issues/PRを操作するためのツール群。
gh CLI を利用する。
"""

import json
import subprocess

REPO = "chanceai1234-glitch/uranai-mura"


def _run_gh(args: list[str]) -> str:
    """gh CLIコマンドを実行する。"""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"gh command failed: {result.stderr}")
    return result.stdout.strip()


def create_issue(title: str, body: str, labels: list[str] | None = None) -> dict:
    """GitHub Issueを作成する。

    Args:
        title: Issueタイトル
        body: Issue本文（Markdown）
        labels: ラベルのリスト

    Returns:
        {"number": int, "url": str}
    """
    args = ["issue", "create", "--repo", REPO, "--title", title, "--body", body]
    if labels:
        for label in labels:
            args.extend(["--label", label])
    output = _run_gh(args)
    # gh issue create は URL を返す
    return {"url": output}


def list_issues(
    state: str = "open",
    labels: list[str] | None = None,
    limit: int = 30,
) -> list[dict]:
    """Issueの一覧を取得する。

    Args:
        state: "open", "closed", "all"
        labels: フィルタするラベル
        limit: 取得件数

    Returns:
        Issueのリスト
    """
    args = [
        "issue", "list", "--repo", REPO,
        "--state", state,
        "--limit", str(limit),
        "--json", "number,title,state,labels,assignees,url",
    ]
    if labels:
        args.extend(["--label", ",".join(labels)])
    output = _run_gh(args)
    return json.loads(output) if output else []


def create_pr(
    title: str,
    body: str,
    head: str,
    base: str = "main",
) -> dict:
    """Pull Requestを作成する。

    Args:
        title: PRタイトル
        body: PR本文（Markdown）
        head: ソースブランチ
        base: ターゲットブランチ

    Returns:
        {"url": str}
    """
    args = [
        "pr", "create", "--repo", REPO,
        "--title", title,
        "--body", body,
        "--head", head,
        "--base", base,
    ]
    output = _run_gh(args)
    return {"url": output}


def review_pr(pr_number: int, body: str, event: str = "COMMENT") -> str:
    """PRにレビューコメントを投稿する。

    Args:
        pr_number: PR番号
        body: レビューコメント
        event: "COMMENT", "APPROVE", "REQUEST_CHANGES"

    Returns:
        結果メッセージ
    """
    args = [
        "pr", "review", str(pr_number),
        "--repo", REPO,
        "--body", body,
    ]
    event_flags = {
        "APPROVE": "--approve",
        "REQUEST_CHANGES": "--request-changes",
        "COMMENT": "--comment",
    }
    args.append(event_flags.get(event, "--comment"))
    return _run_gh(args)


def add_comment(issue_number: int, body: str) -> str:
    """Issue/PRにコメントを追加する。

    Args:
        issue_number: Issue/PR番号
        body: コメント本文

    Returns:
        結果メッセージ
    """
    args = [
        "issue", "comment", str(issue_number),
        "--repo", REPO,
        "--body", body,
    ]
    return _run_gh(args)
