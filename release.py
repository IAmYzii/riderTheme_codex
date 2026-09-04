"""Build the jar and publish it through this repository as a custom JetBrains plugin repository.

The jar is committed under repo/ and served by raw.githubusercontent.com; repo/updatePlugins.xml is the
repository descriptor that Rider polls (Settings > Plugins > Manage Plugin Repositories).

    py -3 release.py            # build, write repo/, commit "Release x.y.z", tag vx.y.z
    git push --follow-tags      # publish (Rider picks the new version up on its next plugin check)

Bump <version> in src/META-INF/plugin.xml (and the change notes) before running.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_DIR = ROOT / "repo"
PLUGIN_ID = "com.patprochazka.risecodex"


def sh(*args, check=True):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=check).stdout.strip()


def github_slug():
    url = sh("git", "remote", "get-url", "origin", check=False)
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", url)
    if not m:
        sys.exit("origin is not a GitHub remote - add it first: git remote add origin https://github.com/<owner>/rise-codex-theme.git")
    return m.group(1), m.group(2)


def main():
    subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=ROOT, check=True)
    plugin_xml = (ROOT / "src" / "META-INF" / "plugin.xml").read_text(encoding="utf-8")
    version = re.search(r"<version>([^<]+)</version>", plugin_xml).group(1)
    since = re.search(r'since-build="([^"]+)"', plugin_xml).group(1)
    notes = re.search(r"<change-notes><!\[CDATA\[(.*?)\]\]></change-notes>", plugin_xml, re.S)
    jar = ROOT / "dist" / f"rise-codex-theme-{version}.jar"
    owner, repo = github_slug()
    branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD") or "main"

    REPO_DIR.mkdir(exist_ok=True)
    for old in REPO_DIR.glob("rise-codex-theme-*.jar"):
        old.unlink()
    shutil.copy2(jar, REPO_DIR / jar.name)
    jar_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/repo/{jar.name}"
    descriptor = f"""<?xml version="1.0" encoding="UTF-8"?>
<plugins>
  <plugin id="{PLUGIN_ID}" url="{jar_url}" version="{version}">
    <idea-version since-build="{since}" />
    <name>Rise Codex Theme</name>
    <vendor>Pat Prochazka</vendor>
    <description><![CDATA[Dark, disciplined IDE theme: aged iron, oxidized brass, parchment, candlelight, sealing wax.]]></description>
    <change-notes><![CDATA[{notes.group(1).strip() if notes else ""}]]></change-notes>
  </plugin>
</plugins>
"""
    (REPO_DIR / "updatePlugins.xml").write_text(descriptor, encoding="utf-8")
    repo_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/repo/updatePlugins.xml"

    sh("git", "add", "-A")
    if sh("git", "status", "--porcelain"):
        sh("git", "commit", "-q", "-m", f"Release {version}")
    tags = sh("git", "tag", "--list", f"v{version}")
    if not tags:
        sh("git", "tag", "-a", f"v{version}", "-m", f"Release {version}")
    print(f"release {version} committed and tagged.")
    print(f"plugin repository URL for Rider: {repo_url}")
    print("publish with: git push --follow-tags")


if __name__ == "__main__":
    main()
