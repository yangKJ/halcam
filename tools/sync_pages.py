#
#  sync_pages.py
#  HAL 官网
#
#  Created by Condy on 2026/11/17.
#

"""从 App 唯一法律正文及官网支持正文导出无依赖静态页面。"""

import argparse
import html
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://yangkj.github.io/halcam"
PAGES = {
    "privacy-policy": ("Privacy", "隐私政策", "Privacy Policy"),
    "terms-of-service": ("Terms", "用户协议", "Terms of Use"),
    "support": ("Support", "技术支持", "Support"),
}


def inline(text):
    escaped = html.escape(text)
    return re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)


def render_markdown(source):
    blocks, paragraph, headings = [], [], []
    in_list = False

    def flush():
        if paragraph:
            blocks.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    for line in source.splitlines() + [""]:
        if line.startswith("<!--"):
            continue
        if not line.startswith("- ") and in_list:
            blocks.append("</ul>")
            in_list = False
        if not line.strip():
            flush()
        elif line.startswith("# "):
            flush()
            blocks.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            flush()
            anchor = f"section-{len(headings) + 1}"
            headings.append((anchor, line[3:]))
            blocks.append(f'<h2 id="{anchor}">{inline(line[3:])}</h2>')
        elif line.startswith("- "):
            flush()
            if not in_list:
                blocks.append("<ul>")
                in_list = True
            blocks.append(f"<li>{inline(line[2:])}</li>")
        else:
            paragraph.append(line)
    return "\n".join(blocks), headings


def page_html(slug, language, source):
    chinese = language == "zh"
    title = PAGES[slug][1 if chinese else 2]
    other = "en" if chinese else "zh"
    body, headings = render_markdown(source)
    introduction, sections = body.split("<h2", 1)
    sections = "<h2" + sections
    nav = "\n".join(
        f'<a href="{key}.html"' + (' aria-current="page"' if key == slug else "")
        + f'>{values[1 if chinese else 2]}</a>'
        for key, values in PAGES.items()
    )
    toc = "".join(f'<li><a href="#{anchor}">{html.escape(text)}</a></li>' for anchor, text in headings)
    return f'''<!doctype html>
<!-- 作者：Condy。由 tools/sync_pages.py 导出，请修改正文源文件。 -->
<html lang="{'zh-Hans' if chinese else 'en'}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="author" content="Condy">
    <title>HAL {html.escape(title)}</title>
    <meta name="description" content="{'HAL 相机的' + title + '。联系开发者，了解本地数据、权限与购买。' if chinese else 'HAL camera ' + title.lower() + '. Contact the developer and understand local data, permissions, and purchases.'}">
    <meta name="color-scheme" content="light">
    <link rel="canonical" href="{BASE_URL}/{language}/{slug}.html">
    <link rel="alternate" hreflang="zh-Hans" href="{BASE_URL}/zh/{slug}.html">
    <link rel="alternate" hreflang="en" href="{BASE_URL}/en/{slug}.html">
    <link rel="stylesheet" href="../assets/pages.css">
</head>
<body>
    <a class="skip-link" href="#main">{'跳到正文' if chinese else 'Skip to content'}</a>
    <header class="site-header">
        <span class="brand" aria-label="HAL Cam"><span class="brand-mark" aria-hidden="true"></span>HAL<span class="brand-label">CAM</span></span>
        <nav aria-label="{'主要导航' if chinese else 'Main navigation'}">{nav}
            <a class="language" href="../{other}/{slug}.html" lang="{other}" hreflang="{other}">{'EN' if chinese else '中文'}</a>
        </nav>
    </header>
    <main id="main" class="document">
        <p class="eyebrow">HAL CAM <span aria-hidden="true">/</span> {PAGES[slug][2].upper()}</p>
        <article>
            {introduction}
            <details class="contents"><summary>{'本页目录' if chinese else 'On this page'}</summary><ol>{toc}</ol></details>
            {sections}
        </article>
        <section class="contact" aria-label="{'联系支持' if chinese else 'Contact support'}">
            <p>{'还有疑问？' if chinese else 'Still have a question?'}</p>
            <a href="mailto:yangkj310@gmail.com">yangkj310@gmail.com <span aria-hidden="true">↗</span></a>
        </section>
    </main>
    <footer class="site-footer"><span>© 2026 HAL</span><span>{'留住你喜欢的每一刻。' if chinese else 'Keep the moments you love.'}</span></footer>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("legal_source", type=Path, help="HAL App 的 Resources/Legal 目录")
    parser.add_argument("--check", action="store_true", help="仅核对导出页面与正文一致")
    args = parser.parse_args()
    for language, suffix in [("zh", "zh-Hans"), ("en", "en")]:
        for slug, values in PAGES.items():
            source = (ROOT / "content" / f"support.{suffix}.md" if slug == "support"
                      else args.legal_source / f"{values[0]}.{suffix}.md")
            expected = page_html(slug, language, source.read_text(encoding="utf-8"))
            destination = ROOT / "docs" / language / f"{slug}.html"
            if args.check:
                if not destination.exists() or destination.read_text(encoding="utf-8") != expected:
                    raise SystemExit(f"页面与正文不一致：{destination}")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(expected, encoding="utf-8")
    print("6 个中英文页面与正文一致。" if args.check else "已导出 6 个中英文页面。")


if __name__ == "__main__":
    main()
