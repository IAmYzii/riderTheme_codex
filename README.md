# Rise Codex — Rider theme

Dark, disciplined JetBrains theme built from `rise_codex_ide_theme_spec.md`: aged iron, oxidized brass,
parchment, candlelight, sealing wax. UI theme (Islands look) + editor colour scheme + icon palette.

*IN CODEX VERITAS*

## Layout

```
palette.py            single source of truth (spec tokens, amendments, ramps, source-colour maps)
gen.py                generates src/rise-codex.theme.json and src/RiseCodex.xml from ref/ + palette
build.py              gen + lint (no #000000/#FFFFFF, token refs, metadata keys) + contrast table + jar
apply.py              installs the jar and activates the theme in Rider2026.2 and Rider2026.1 (Rider closed)
tools/extract_refs.py pulls the reference theme/scheme/metadata/icon colours out of the Rider install
ref/                  extracted references (Islands Dark theme JSON, Rider Islands Dark scheme, metadata)
src/                  plugin sources (META-INF/plugin.xml, theme JSON, scheme XML, icon)
dist/                 rise-codex-theme-<version>.jar
preview/preview.html  static mock of the IDE with the palette applied
backup/<timestamp>/   copies of every config file apply.py touched
SPEC-AMENDMENTS.md    accepted deviations from the spec and why
```

## Build and install

```bash
py -3 build.py            # regenerate, lint, contrast report, dist/rise-codex-theme-1.0.0.jar
py -3 apply.py            # Rider must be closed; --no-font / --no-profile / --force
```

Manual alternative: Settings → Plugins → ⚙ → Install Plugin from Disk → `dist/rise-codex-theme-1.0.0.jar`,
restart, then Settings → Appearance & Behavior → Appearance → Theme: **Rise Codex** (the editor scheme
switches with it).

## Sharing between machines (custom plugin repository)

JetBrains Backup and Sync only reinstalls Marketplace plugins, so this repo doubles as a plugin repository:

```bash
py -3 release.py          # build, copy the jar to repo/, write repo/updatePlugins.xml, commit + tag
git push --follow-tags    # publish
```

On every machine, once: Settings → Plugins → ⚙ → Manage Plugin Repositories → add
`https://raw.githubusercontent.com/IAmYzii/riderTheme_codex/main/repo/updatePlugins.xml`, then install
"Rise Codex Theme" from the Marketplace tab (updates arrive like any other plugin). Theme/scheme selection
syncs via Backup and Sync; the UI font (Cambria 14) is per machine — set it in Appearance or run `apply.py`.

## How the generation works

- **UI**: the bundled `Islands Dark` theme JSON is reused as-is; only its named palette is replaced
  (`palette.islands_colors()`), literal hex values are remapped (`UI_SOURCE_MAP`, then hue-family
  fallback `materialize()`), and a few keys are overridden (`gen.UI_OVERRIDES`).
- **Editor scheme**: the bundled `Rider Islands Dark` scheme (all ReSharper/Unity/ShaderLab keys) is
  remapped by semantic role (`SCHEME_SOURCE_MAP`: Rider's keyword blue → lit rust, type purple → brass,
  method teal → candle gold, …), then explicit overrides (`gen.ATTR_OVERRIDES`, `gen.COLOR_OVERRIDES`).
  Anything not covered falls back to `materialize()`, so no cold hue can leak in.
- **Icons**: every colour used by the new-UI SVG icons (`ref/icon-colors.json`) is mapped in
  `icons.ColorPalette` (`ICON_SOURCE_MAP` + fallback), plus the classic named palette for old-style icons.

## Tuning

0. `palette.TEXT_LIFT` (0 = spec values, 0.5 = current, 1 = full lift) lightens and saturates all text
   tokens at once; `gen.UI_OVERRIDES["Island.inactiveAlpha"]` controls how much unfocused islands are dimmed.
1. Change a value in `palette.py` (or an override in `gen.py`), run `py -3 build.py`, run `py -3 apply.py`
   with Rider closed (or reinstall the jar from disk) and restart Rider.
2. Editor colours can also be tuned live in Settings → Editor → Color Scheme; Rider stores the diff in
   `%APPDATA%\JetBrains\Rider2026.2\colors\_@user_Rise Codex.icls` — fold the values back into `palette.py`.
3. The UI font is a global Rider setting (Appearance → Use custom font), not part of the theme.

## Rollback

Restore the files from `backup/<timestamp>/` (laf.xml, colors.scheme.xml, other.xml, PowerShell profile)
while Rider is closed, or simply pick another theme in Appearance. Delete
`plugins/rise-codex-theme-*.jar` to uninstall.

## Palette

| Token | Hex | Use |
|---|---|---|
| void | `#0B0908` | window frame, terminal background |
| obsidian | `#110E0C` | editor |
| iron | `#181310` | tool windows, popups, dialogs |
| raised iron | `#211A15` | hover, active tab |
| selected iron | `#2A211A` | inactive selection, usages |
| border | `#3B2D22` | borders, separators |
| bronze | `#6E5033` | focus, accent, scrollbar, tab underline |
| old gold | `#A37843` | strings, constants, warnings stripe, primary accent |
| candle gold | `#C09152` | methods, caret, links, active tab text |
| parchment | `#C7AE87` | editor and UI text |
| old paper | `#9E8768` | parameters, operators, secondary text |
| ash | `#75685A` | comments, disabled |
| faded ink | `#50463C` | line numbers, guides, disabled |
| lit rust | `#B9663D` | keywords (amended from `#9A5635`) |
| copper | `#B87545` | attributes, escapes, events |
| brass (lifted) | `#8E8663` | types (amended from `#77704E`) |
| oxidized brass | `#77704E` | success, run button, ANSI green |
| cold steel | `#748080` | numbers, debugger values, ANSI blue |
| wax | `#783A32` | error base, stop button |
| ember | `#A14D3E` | error squiggle/stripe |
| ember bright | `#B75A49` | error text |
| faded gold | `#806C50` | doc comments, ANSI magenta |
