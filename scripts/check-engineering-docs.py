"""检查工程文档链接、22 张图的导出、编号和自动导出内容是否与源码一致。"""

import os
import json
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/software-engineering"
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def canonical_text(path):
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def headings(path):
    result = set()
    counts = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            continue
        title = re.sub(r"^#+\s+", "", line).strip().lower()
        title = re.sub(r"[^\w\-\s\u4e00-\u9fff]", "", title)
        slug = re.sub(r"\s", "-", title)
        index = counts.get(slug, 0)
        counts[slug] = index + 1
        result.add(slug if index == 0 else f"{slug}-{index}")
    return result


markdown = sorted(DOCS.rglob("*.md")) + [ROOT / "README.md"]
link_count = 0
for path in markdown:
    text = path.read_text(encoding="utf-8")
    for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        link = link.strip("<>")
        if link.startswith(("https://", "http://", "mailto:")):
            continue
        target, _, fragment = unquote(link).partition("#")
        resolved = (path.parent / target).resolve() if target else path
        link_count += 1
        check(resolved.exists(), f"Missing link: {path.relative_to(ROOT)} -> {link}")
        if not resolved.is_file() or not fragment:
            continue
        if resolved.suffix == ".md":
            check(fragment in headings(resolved), f"Missing heading: {path.relative_to(ROOT)} -> {link}")
        elif re.fullmatch(r"L\d+", fragment):
            check(int(fragment[1:]) <= len(resolved.read_text(encoding="utf-8").splitlines()), f"Invalid source line: {link}")

diagram_rows = re.findall(r"^\| (F\d{2}) \|", (DOCS / "README.md").read_text(encoding="utf-8"), re.M)
expected = {f"F{i:02d}" for i in range(1, 23)}
check(len(diagram_rows) == 22 and set(diagram_rows) == expected, "Figure index must contain F01 through F22 exactly once")
sources = sorted((DOCS / "diagrams/src").glob("F*"))
check(len(sources) == 22, "Expected 22 diagram source files")
manifest_path = DOCS / "diagrams/render-manifest.json"
check(manifest_path.exists(), "Missing render manifest; rerun diagram renderer")
manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
entries = {entry["source"]: entry for entry in manifest.get("figures", [])}
check(manifest.get("schema") == 2, "Unsupported render manifest schema")
style_digest = hashlib.sha256(canonical_text(DOCS / "diagrams/src/_style.puml")).hexdigest()
check(manifest.get("sharedStyleSha256") == style_digest, "Shared diagram style changed; rerender diagrams")
check(len(entries) == 22, "Render manifest must contain 22 figures")
for source in sources:
    entry = entries.get(source.name, {})
    check(entry.get("sourceSha256") == hashlib.sha256(canonical_text(source)).hexdigest(), f"Diagram source changed since render: {source.name}")
    check(source.stem[:3] in expected, f"Unknown figure: {source.name}")
    check(source.stem[:3] in source.read_text(encoding="utf-8"), f"Figure number absent in source: {source.name}")
    for suffix in ["svg", "png"]:
        target = DOCS / "diagrams" / suffix / (source.stem + "." + suffix)
        check(target.exists(), f"Missing diagram export: {target.name}")
        if not target.exists():
            continue
        content = canonical_text(target) if suffix == "svg" else target.read_bytes()
        check(entry.get(suffix + "Sha256") == hashlib.sha256(content).hexdigest(), f"Diagram image differs from render manifest: {target.name}")
        if suffix == "svg":
            root = ElementTree.fromstring(target.read_bytes())
            check(root.tag.endswith("svg"), f"Invalid SVG root: {target.name}")
            text = " ".join(root.itertext())
            check(source.stem[:3] in text, f"Figure number absent in SVG: {target.name}")
            check("Syntax Error" not in text and "An error has occured" not in text, f"Renderer error image: {target.name}")
            check(not any(node.tag.endswith("script") for node in root.iter()), f"Unexpected script in SVG: {target.name}")
        else:
            with Image.open(target) as picture:
                picture.verify()

with tempfile.TemporaryDirectory(prefix="smarthire-engineering-check-") as directory:
    environment = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/export-engineering-reference.py"), "--output-root", directory],
        cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8",
    )
    check(result.returncode == 0, "Reference export failed")
    if result.returncode == 0:
        for relative in [
            "reference/database-dictionary.md", "reference/api-inventory.md", "reference/test-inventory.md",
            "diagrams/src/F10-database-er.dot",
        ]:
            check(canonical_text(DOCS / relative) == canonical_text(Path(directory) / relative), f"Generated reference is stale: {relative}")
        print(result.stdout.strip())

for error in errors:
    print(error)
print(f"Checked {len(markdown)} Markdown files, {link_count} local links, 22 diagram sources and 44 images.")
print("ENGINEERING_DOCS_VALID=" + str(not errors))
sys.exit(1 if errors else 0)
