"""Extract reference files from the installed Rider (read-only) into ref/ and tally icon + scheme colors."""
import json, re, zipfile
from collections import Counter
from pathlib import Path

RIDER = Path(r"C:\Program Files\JetBrains\JetBrains Rider 2026.2.1")
ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "ref"
REF.mkdir(exist_ok=True)

def extract(jar, entry, dest):
    with zipfile.ZipFile(jar) as z:
        data = z.read(entry)
    (REF / dest).write_bytes(data)
    print(f"extracted {dest} ({len(data)} B)")

ide = RIDER / "lib" / "intellij.platform.ide.impl.jar"
pack = RIDER / "plugins" / "rider-theme-pack" / "lib" / "rider-theme-pack.jar"
extract(ide, "themes/islands/ManyIslandsDark.theme.json", "ManyIslandsDark.theme.json")
extract(ide, "themes/expUI/expUI_dark.theme.json", "expUI_dark.theme.json")
extract(ide, "themes/metadata/IntelliJPlatform.themeMetadata.json", "IntelliJPlatform.themeMetadata.json")
extract(ide, "DefaultColorSchemesManager.xml", "DefaultColorSchemesManager.xml")
extract(pack, "colorSchemes/RiderIslandsDark.xml", "RiderIslandsDark.xml")
extract(pack, "RiderDark.theme.json", "RiderDark.theme.json")

# --- icon colors used in dark mode (expui *_dark.svg + plain svgs lacking a _dark sibling)
svgs = {}
jars = list((RIDER / "lib").glob("*.jar")) + list((RIDER / "plugins").rglob("*.jar"))
for jar in jars:
    try:
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                if n.endswith(".svg") and "expui/" in n:
                    svgs.setdefault(n, jar)
    except zipfile.BadZipFile:
        pass
names = set(svgs)
used = [n for n in names if n.endswith("_dark.svg") or (n[:-4] + "_dark.svg") not in names]
byjar = {}
for n in used:
    byjar.setdefault(svgs[n], []).append(n)
counts = Counter()
files_per_color = Counter()
for jar, entries in byjar.items():
    with zipfile.ZipFile(jar) as z:
        for n in entries:
            t = z.read(n).decode("utf-8", "replace")
            found = set()
            for m in re.finditer(r"#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?![0-9A-Fa-f])", t):
                counts[m.group(0)] += 1
                found.add(m.group(0))
            for c in found:
                files_per_color[c] += 1
icon_colors = [{"color": c, "occurrences": counts[c], "files": files_per_color[c]} for c in counts]
icon_colors.sort(key=lambda d: -d["occurrences"])
(REF / "icon-colors.json").write_text(json.dumps(icon_colors, indent=1))
print(f"icon svgs considered: {len(used)} of {len(names)}; distinct colors: {len(icon_colors)}")
for d in icon_colors[:60]:
    print(f"  {d['color']:<10} occ={d['occurrences']:<5} files={d['files']}")

# --- scheme colors histogram (attribute values + <colors>)
xml = (REF / "RiderIslandsDark.xml").read_text(encoding="utf-8")
sc = Counter()
for m in re.finditer(r'name="(FOREGROUND|BACKGROUND|EFFECT_COLOR|ERROR_STRIPE_COLOR)" value="([^"]+)"', xml):
    sc[m.group(2).lstrip("#").upper()] += 1
colors_block = re.search(r"<colors>(.*?)</colors>", xml, re.S).group(1)
for m in re.finditer(r'value="([^"]+)"', colors_block):
    sc[m.group(1).lstrip("#").upper()] += 1
(REF / "scheme-colors.json").write_text(json.dumps(sc.most_common(), indent=1))
print(f"scheme distinct colors: {len(sc)}")
for c, n in sc.most_common(80):
    print(f"  {c:<9} {n}")

# --- literal hex values in the ui section of ManyIslandsDark
theme = json.loads((REF / "ManyIslandsDark.theme.json").read_text(encoding="utf-8"))
lit = Counter()
paths = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + [k])
    elif isinstance(node, str) and node.startswith("#"):
        lit[node] += 1
        paths.append((".".join(path), node))
walk(theme["ui"], [])
print(f"ui literal hexes: {len(paths)} occurrences, {len(lit)} distinct")
for p, v in paths:
    print(f"  {p} = {v}")
# colors referenced in ui but missing from colors
names_in_colors = set(theme["colors"])
refs = Counter()
def walk2(node):
    if isinstance(node, dict):
        for v in node.values():
            walk2(v)
    elif isinstance(node, str) and not node.startswith("#"):
        refs[node] += 1
walk2(theme["ui"])
missing = [r for r in refs if r not in names_in_colors and re.fullmatch(r"[a-z0-9-]+", r)]
print("ui refs not in colors (probably plain strings):", missing[:40])
