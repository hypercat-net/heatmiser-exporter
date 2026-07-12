#!/usr/bin/env python3
"""Build a static documentation site for GitHub Pages."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GUIDE = DOCS / "guide"
DEFAULT_OUT = ROOT / "site"

NAV = [
    ("Home", "index.html", 0),
    ("Install", "install.html", 0),
    ("Metrics", "metrics.html", 0),
]


def nav_html(prefix: str = "") -> str:
    links = []
    for label, href, _ in NAV:
        links.append(f'<a href="{prefix}{href}">{label}</a>')
    return "\n        ".join(links)


SITE_CSS = """
:root {
  --ink: #1a1f24;
  --muted: #5b6570;
  --bg: #f6f3ee;
  --accent: #0b6e4f;
  --line: #ddd4c6;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --sans: "IBM Plex Sans", "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--sans);
  color: var(--ink);
  background:
    radial-gradient(1200px 500px at 10% -10%, #e7f3ec 0%, transparent 55%),
    linear-gradient(180deg, #fbf8f2, var(--bg));
  line-height: 1.55;
}
.wrap { width: min(960px, calc(100% - 2rem)); margin: 0 auto; }
.top {
  border-bottom: 1px solid var(--line);
  background: rgba(255,253,249,0.92);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}
.top .wrap {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  min-height: 3.25rem;
}
.brand {
  font-weight: 700;
  color: var(--ink);
  text-decoration: none;
  letter-spacing: -0.02em;
}
nav { display: flex; flex-wrap: wrap; gap: 0.85rem; }
nav a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.95rem;
}
nav a:hover { color: var(--accent); }
.prose { padding: 2rem 0 4rem; }
.prose h1, .prose h2, .prose h3 { line-height: 1.2; letter-spacing: -0.02em; }
.prose a { color: var(--accent); }
.prose code, .prose pre {
  font-family: var(--mono);
  font-size: 0.9em;
}
.prose pre {
  background: #182028;
  color: #e8eef4;
  padding: 1rem 1.1rem;
  overflow: auto;
  border-radius: 10px;
}
.prose table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.92rem;
}
.prose th, .prose td {
  border: 1px solid var(--line);
  padding: 0.45rem 0.6rem;
  vertical-align: top;
}
.prose th { background: #efe8dc; text-align: left; }
.prose blockquote {
  border-left: 3px solid var(--accent);
  margin-left: 0;
  padding-left: 1rem;
  color: var(--muted);
}
.prose ul { padding-left: 1.25rem; }
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — heatmiser-exporter</title>
  <link rel="stylesheet" href="{prefix}assets/site.css" />
</head>
<body>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="{prefix}index.html">heatmiser-exporter</a>
      <nav>
        {nav}
      </nav>
    </div>
  </header>
  <main class="wrap prose">
{body}
  </main>
</body>
</html>
"""


def render_markdown(path: Path) -> str:
    return markdown.markdown(
        path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "toc"],
    )


def write_page(out: Path, rel: str, title: str, body: str, *, depth: int = 0) -> None:
    prefix = "../" * depth
    html = PAGE.format(
        title=title,
        prefix=prefix,
        nav=nav_html(prefix),
        body=body,
    )
    target = out / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    (out / "assets").mkdir()
    (out / "assets" / "site.css").write_text(SITE_CSS, encoding="utf-8")

    guides = [
        ("index.md", "index.html", "Home", 0),
        ("install.md", "install.html", "Install", 0),
        ("metrics.md", "metrics.html", "Metrics", 0),
    ]
    for src_name, dest, title, depth in guides:
        src = GUIDE / src_name
        if not src.exists():
            raise SystemExit(f"Missing guide page: {src}")
        write_page(out, dest, title, render_markdown(src), depth=depth)

    print(f"Built site → {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output directory (default: ./site)",
    )
    args = parser.parse_args()
    build(args.out.resolve())


if __name__ == "__main__":
    main()
