"""Generate, validate, lint, report contrast, and package the Rise Codex theme plugin jar."""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import gen
import palette as P

ROOT = Path(__file__).resolve().parent
SRC, DIST, REF = ROOT / "src", ROOT / "dist", ROOT / "ref"

HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?")
TOKEN_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")


def flatten(node, prefix=""):
    out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    else:
        out[prefix] = node
    return out


def main():
    gen.main()
    problems = []
    warnings = []

    theme_text = (SRC / "rise-codex.theme.json").read_text(encoding="utf-8")
    theme = json.loads(theme_text)

    # 1. forbidden pure black / white anywhere in the theme and scheme (values only; icon palette keys are
    #    the source colours being replaced, so they legitimately contain black and white)
    def check_values(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                check_values(v, f"{path}.{k}")
        elif isinstance(node, str):
            for m in HEX_RE.finditer(node):
                if m.group(0)[1:7].upper() in ("000000", "FFFFFF"):
                    problems.append(f"theme.json {path} contains forbidden colour {m.group(0)}")

    check_values({k: v for k, v in theme.items() if k != "icons"}, "theme")
    check_values(theme["icons"]["ColorPalette"], "theme.icons.ColorPalette")
    scheme_text = (SRC / "RiseCodex.xml").read_text(encoding="utf-8")
    for m in re.finditer(r'value="#?([0-9A-Fa-f]{6})(?:[0-9A-Fa-f]{2})?"', scheme_text):
        if m.group(1).upper() in ("000000", "FFFFFF"):
            problems.append(f"RiseCodex.xml contains forbidden colour {m.group(0)}")

    # 2. every token reference resolves (colors -> colors, ui -> colors)
    colors = theme["colors"]

    def resolve(name, seen=()):
        if name in seen:
            problems.append(f"colour token cycle: {' -> '.join(seen + (name,))}")
            return None
        v = colors.get(name)
        if v is None:
            return None
        return v if v.startswith("#") else resolve(v, seen + (name,))

    for name in colors:
        if resolve(name) is None:
            problems.append(f"colour token '{name}' does not resolve")
    flat_ui = flatten(theme["ui"])
    for key, val in flat_ui.items():
        if isinstance(val, str) and not val.startswith("#") and TOKEN_RE.match(val):
            if val not in colors:
                problems.append(f"ui.{key} references unknown token '{val}'")

    # 3. ui keys: everything not in the reference theme must exist in the platform metadata
    ref = json.loads((REF / "ManyIslandsDark.theme.json").read_text(encoding="utf-8"))
    ref_keys = set(flatten(ref["ui"]))
    meta = json.loads((REF / "IntelliJPlatform.themeMetadata.json").read_text(encoding="utf-8"))
    meta_keys = {e["key"] for e in meta.get("ui", [])}
    for key in flat_ui:
        if key not in ref_keys and key not in meta_keys:
            warnings.append(f"ui key '{key}' is neither in Islands Dark nor in platform metadata")

    # 4. icon palette values must be hex
    for k, v in theme["icons"]["ColorPalette"].items():
        if not HEX_RE.fullmatch(v):
            problems.append(f"icon palette {k} -> {v} is not a hex colour")

    # 5. scheme XML well-formed + required keys present
    root = ET.fromstring(scheme_text)
    names = {o.get("name") for o in root.find("attributes").findall("option")}
    for req in ("TEXT", "DEFAULT_KEYWORD", "DEFAULT_CLASS_NAME", "DEFAULT_FUNCTION_CALL", "DEFAULT_STRING",
                "DEFAULT_NUMBER", "DEFAULT_LINE_COMMENT", "ERRORS_ATTRIBUTES", "CONSOLE_RED_OUTPUT"):
        if req not in names:
            problems.append(f"scheme missing {req}")
    if root.get("name") != gen.SCHEME_NAME:
        problems.append("scheme name mismatch")

    # 6. contrast report
    rows = [
        ("editor text (parchment)", P.PARCHMENT, P.OBSIDIAN, 4.5),
        ("keywords (lit rust)", P.KEYWORD, P.OBSIDIAN, 4.5),
        ("spec keywords (rust) - not used", P.RUST, P.OBSIDIAN, 0),
        ("types (lifted brass)", P.TYPE, P.OBSIDIAN, 4.5),
        ("spec types (oxidized brass) - not used", P.OXIDIZED_BRASS, P.OBSIDIAN, 0),
        ("methods (candle gold)", P.CANDLE_GOLD, P.OBSIDIAN, 4.5),
        ("strings / constants (old gold)", P.OLD_GOLD, P.OBSIDIAN, 4.5),
        ("parameters / operators (old paper)", P.OLD_PAPER, P.OBSIDIAN, 4.5),
        ("numbers (cold steel)", P.COLD_STEEL, P.OBSIDIAN, 4.5),
        ("attributes / escapes (copper)", P.COPPER, P.OBSIDIAN, 4.5),
        ("comments (ash)", P.ASH, P.OBSIDIAN, 3.0),
        ("doc comments (faded gold)", P.FADED_GOLD, P.OBSIDIAN, 3.0),
        ("line numbers (faded ink) - intentionally faint", P.FADED_INK, P.OBSIDIAN, 0),
        ("error text (ember bright)", P.ERROR_TEXT, P.IRON, 3.0),
        ("UI text (parchment on iron)", P.PARCHMENT, P.IRON, 4.5),
        ("UI secondary (old paper on iron)", P.OLD_PAPER, P.IRON, 3.0),
        ("UI disabled (faded ink on iron)", P.FADED_INK, P.IRON, 0),
        ("UI link (candle gold on iron)", P.CANDLE_GOLD, P.IRON, 4.5),
        ("button text (bright parchment on bronze)", P.BRIGHT_PARCHMENT, P.BRONZE, 3.0),
        ("selected row text (parchment on selection)", P.PARCHMENT, P.SELECTION, 3.0),
        ("terminal fg (parchment on void)", P.PARCHMENT, P.VOID, 4.5),
        ("terminal blue vs cyan difference", P.COLD_STEEL, P.CYAN_SUB, 0),
    ]
    print("\nContrast (WCAG):")
    for label, fg, bg, minimum in rows:
        c = P.contrast(fg, bg)
        flag = ""
        if minimum and c < minimum:
            flag = f"  <-- below {minimum}"
            problems.append(f"contrast {label}: {c:.2f} < {minimum}")
        print(f"  {c:5.2f}  {label} ({fg} on {bg}){flag}")

    for w in warnings:
        print("WARN:", w)
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    # 7. package
    version = re.search(r"<version>([^<]+)</version>", (SRC / "META-INF" / "plugin.xml").read_text(encoding="utf-8")).group(1)
    DIST.mkdir(exist_ok=True)
    jar = DIST / f"rise-codex-theme-{version}.jar"
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SRC.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(SRC).as_posix())
    with zipfile.ZipFile(jar) as z:
        entries = z.namelist()
    print(f"\nbuilt {jar} ({jar.stat().st_size} B):")
    for e in entries:
        print("  ", e)
    assert "META-INF/plugin.xml" in entries and "rise-codex.theme.json" in entries and "RiseCodex.xml" in entries


if __name__ == "__main__":
    main()
