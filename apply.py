"""Activate the Rise Codex theme in the Rider configurations (run only while Rider is closed).

Steps per configuration directory:
  1. copy dist/rise-codex-theme-<version>.jar into plugins/ (older copies removed)
  2. options/laf.xml         -> <laf themeId="com.patprochazka.risecodex.dark"/> + laf-to-scheme entry
  3. options/colors.scheme.xml -> <global_color_scheme name="Rise Codex"/>
  4. options/other.xml       -> NotRoamableUiSettings.fontFace = Cambria (overrideLafFonts = true)
Then appends a guarded greeting block to the Windows PowerShell profile (once).
Every touched file is backed up to backup/<timestamp>/ first. Use --force to skip the running-Rider check,
--no-font to keep the current UI font, --no-profile to leave the PowerShell profile alone.
"""
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPDATA = Path.home() / "AppData" / "Roaming"
CONFIGS = [APPDATA / "JetBrains" / "Rider2026.2", APPDATA / "JetBrains" / "Rider2026.1"]
JAR = next(iter(sorted((ROOT / "dist").glob("rise-codex-theme-*.jar"), reverse=True)), None)
THEME_ID = "com.patprochazka.risecodex.dark"
SCHEME_NAME = "Rise Codex"
UI_FONT = "Cambria"
UI_FONT_SIZE = "14.0"   # Cambria has a small x-height; 14 ~ Inter 13
PROFILE = Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
PROFILE_MARKER = "# --- Rise / Codex: greeting inside the JetBrains IDE terminal ---"
PROFILE_BLOCK = f"""
{PROFILE_MARKER}
if ($env:TERMINAL_EMULATOR -eq 'JetBrains-JediTerm') {{
    Write-Host ''
    Write-Host '  IN CODEX VERITAS' -ForegroundColor DarkYellow
    Write-Host ''
}}
# --- end Rise / Codex ---
"""
BACKUP = ROOT / "backup" / time.strftime("%Y%m%d-%H%M%S")


def rider_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq rider64.exe", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    return "rider64.exe" in out


def backup(path):
    if path.exists():
        dest = BACKUP / path.relative_to(Path.home())
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def write_xml(path, root):
    ET.indent(root, space="  ")
    path.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")


def component(root, name):
    for c in root.findall("component"):
        if c.get("name") == name:
            return c
    c = ET.SubElement(root, "component")
    c.set("name", name)
    return c


def apply_laf(cfg):
    path = cfg / "options" / "laf.xml"
    backup(path)
    root = ET.fromstring(path.read_text(encoding="utf-8")) if path.exists() else ET.Element("application")
    laf_mgr = component(root, "LafManager")
    laf_mgr.set("autodetect", "false")
    for old in laf_mgr.findall("laf"):
        laf_mgr.remove(old)
    laf = ET.Element("laf")
    laf.set("themeId", THEME_ID)
    laf_mgr.insert(0, laf)
    prev = laf_mgr.find("lafs-to-previous-schemes")
    if prev is None:
        prev = ET.SubElement(laf_mgr, "lafs-to-previous-schemes")
    for e in prev.findall("laf-to-scheme"):
        if e.get("laf") == THEME_ID:
            prev.remove(e)
    e = ET.SubElement(prev, "laf-to-scheme")
    e.set("laf", THEME_ID)
    e.set("scheme", SCHEME_NAME)
    write_xml(path, root)
    print(f"  laf.xml            -> themeId={THEME_ID}")


def apply_scheme(cfg):
    path = cfg / "options" / "colors.scheme.xml"
    backup(path)
    root = ET.fromstring(path.read_text(encoding="utf-8")) if path.exists() else ET.Element("application")
    comp = component(root, "EditorColorsManagerImpl")
    g = comp.find("global_color_scheme")
    if g is None:
        g = ET.SubElement(comp, "global_color_scheme")
    g.set("name", SCHEME_NAME)
    write_xml(path, root)
    print(f"  colors.scheme.xml  -> {SCHEME_NAME}")


def apply_font(cfg):
    """Textual edit of other.xml (it holds CDATA/JSON blobs of other components, so no XML round-trip)."""
    path = cfg / "options" / "other.xml"
    backup(path)
    text = path.read_text(encoding="utf-8") if path.exists() else "<application>\n</application>\n"
    block_re = re.compile(r'(<component name="NotRoamableUiSettings">)(.*?)(</component>)', re.S)
    m = block_re.search(text)
    if m is None:
        block = (f'  <component name="NotRoamableUiSettings">\n'
                 f'    <option name="fontFace" value="{UI_FONT}" />\n'
                 f'    <option name="fontSize" value="{UI_FONT_SIZE}" />\n'
                 f'    <option name="overrideLafFonts" value="true" />\n'
                 f'  </component>\n')
        text = text.replace("</application>", block + "</application>", 1)
        previous = "(default)"
    else:
        body = m.group(2)
        fm = re.search(r'<option name="fontFace" value="([^"]*)" />', body)
        previous = fm.group(1) if fm else "(default)"
        if fm:
            body = body.replace(fm.group(0), f'<option name="fontFace" value="{UI_FONT}" />', 1)
        else:
            body = f'\n    <option name="fontFace" value="{UI_FONT}" />' + body
        om = re.search(r'<option name="overrideLafFonts" value="([^"]*)" />', body)
        if om:
            body = body.replace(om.group(0), '<option name="overrideLafFonts" value="true" />', 1)
        else:
            body = body.rstrip() + '\n    <option name="overrideLafFonts" value="true" />\n  '
        sm = re.search(r'<option name="fontSize" value="([^"]*)" />', body)
        if sm:
            body = body.replace(sm.group(0), f'<option name="fontSize" value="{UI_FONT_SIZE}" />', 1)
        else:
            body = body.rstrip() + f'\n    <option name="fontSize" value="{UI_FONT_SIZE}" />\n  '
        text = text[:m.start(2)] + body + text[m.end(2):]
    path.write_text(text, encoding="utf-8")
    print(f"  other.xml          -> UI font {previous} -> {UI_FONT} {UI_FONT_SIZE}")


def install_jar(cfg):
    plugins = cfg / "plugins"
    plugins.mkdir(exist_ok=True)
    for old in plugins.glob("rise-codex-theme-*.jar"):
        if old.name != JAR.name:
            old.unlink()
    shutil.copy2(JAR, plugins / JAR.name)
    print(f"  plugins/{JAR.name}")


def apply_profile():
    backup(PROFILE)
    text = PROFILE.read_text(encoding="utf-8") if PROFILE.exists() else ""
    if PROFILE_MARKER in text:
        print("  PowerShell profile: greeting already present")
        return
    PROFILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILE.write_text(text.rstrip("\n") + "\n" + PROFILE_BLOCK, encoding="utf-8")
    print(f"  PowerShell profile: greeting block appended ({PROFILE})")


def main(argv):
    if JAR is None:
        sys.exit("no jar in dist/ - run build.py first")
    if "--force" not in argv and rider_running():
        sys.exit("rider64.exe is still running - close Rider first (or pass --force).")
    BACKUP.mkdir(parents=True, exist_ok=True)
    for cfg in CONFIGS:
        if not (cfg / "options").is_dir():
            print(f"skip {cfg} (no options dir)")
            continue
        print(f"{cfg}:")
        install_jar(cfg)
        apply_laf(cfg)
        apply_scheme(cfg)
        if "--no-font" not in argv:
            apply_font(cfg)
    if "--no-profile" not in argv:
        apply_profile()
    print(f"backups in {BACKUP}")


if __name__ == "__main__":
    main(sys.argv[1:])
