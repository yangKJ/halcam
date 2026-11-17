#
#  check_pages.py
#  HAL 官网
#
#  Created by Condy on 2026/11/17.
#

"""检查静态网页的文档结构、占位文本及本地链接。"""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = set()
        self.errors = []
        self.headings = 0
        self.language = None
        self.charset = False
        self.viewport = False
        self.title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "meta":
            self.charset |= attrs.get("charset", "").lower() == "utf-8"
            self.viewport |= attrs.get("name") == "viewport"
        self.title |= tag == "title"
        self.headings += tag == "h1"
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"重复 ID：{attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "img" and not attrs.get("alt"):
            self.errors.append("图片缺少替代文字")
        for key in ["href", "src", "data-scene-src"]:
            if key in attrs:
                self.references.append(attrs[key])


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "docs").resolve()
    files = sorted(root.rglob("*.html"))
    if not files:
        raise SystemExit("没有找到 HTML 页面")
    pages = {}
    errors = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(source)
        pages[path] = page
        if not all([page.language, page.charset, page.viewport, page.title, page.headings == 1]):
            page.errors.append("语言、字符集、viewport、标题或唯一一级标题不完整")
        if re.search(r"待补充|待定|to be determined|example\.com", source, re.I):
            page.errors.append("存在未完成的占位内容")
        errors.extend(f"{path.relative_to(root)}：{error}" for error in page.errors)
    for path, page in pages.items():
        for reference in page.references:
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                if url.scheme not in ["https", "mailto"]:
                    errors.append(f"不支持的链接：{reference}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                errors.append(f"{path.relative_to(root)}：链接目标不存在 {reference}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{path.relative_to(root)}：锚点不存在 {reference}")
    for css in root.rglob("*.css"):
        for reference in re.findall(r"url\(['\"]?([^)'\"]+)", css.read_text(encoding="utf-8")):
            if not urlsplit(reference).scheme and not (css.parent / reference).resolve().exists():
                errors.append(f"样式资源不存在：{reference}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"{len(files)} 个页面通过结构、占位和本地链接检查。")


if __name__ == "__main__":
    main()
