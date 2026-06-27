from __future__ import annotations


def fmt_int(n) -> str:
    if n is None:
        return "-"
    return f"{int(n):,}"


def fmt_percent(n: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(100.0 * n / total):.1f}%"


def write_or_print(report: str, markdown: str | None) -> int:
    if markdown:
        from .config import expand_path

        out_path = expand_path(markdown)
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote report: {out_path}")
    else:
        print(report)
    return 0
