"""Generate src/rise-codex.theme.json and src/RiseCodex.xml.

theme.json = the bundled Islands Dark `ui` section (ref/ManyIslandsDark.theme.json) with the palette
re-materialised (colors block replaced, literal hexes remapped, targeted overrides, icon palette).
RiseCodex.xml = the bundled Rider Islands Dark scheme (ref/RiderIslandsDark.xml) with every colour
remapped by semantic role (SCHEME_SOURCE_MAP) or hue family (materialize), then explicit overrides.
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import palette as P

ROOT = Path(__file__).resolve().parent
REF = ROOT / "ref"
SRC = ROOT / "src"

THEME_NAME = "Rise Codex"
SCHEME_NAME = "Rise Codex"
AUTHOR = "Pat Prochazka"

FONT_OPTIONS = [  # carried over from the user's current scheme copy (same mechanism as today)
    ("FONT_SCALE", "1.0"),
    ("LINE_SPACING", "1.2"),
    ("EDITOR_FONT_SIZE", "17"),
    ("EDITOR_FONT_NAME", "Iosevka Term"),
    ("EDITOR_LIGATURES", "true"),
]


# =============================================================================== theme.json
def set_ui(ui, dotted, value):
    """Set a flattened key, following the nesting the reference theme already uses."""
    node = ui
    rest = dotted
    while True:
        # longest existing key that is a prefix of `rest`
        candidates = [k for k in node if rest == k or rest.startswith(k + ".")]
        if not candidates:
            break
        k = max(candidates, key=len)
        if rest == k:
            node[k] = value
            return
        if not isinstance(node[k], dict):
            node[k] = value if rest == k else node[k]
            break
        node = node[k]
        rest = rest[len(k) + 1:]
    # create nested structure for the remainder
    parts = rest.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            raise ValueError(f"cannot nest under scalar at {dotted}")
    node[parts[-1]] = value


UI_OVERRIDES = {
    # Islands paints inactive islands at 56 % alpha over the (void) frame, which made every unfocused
    # tool window and the editor look far darker than the mock; keep a subtle focus cue only.
    "Island.inactiveAlpha": 0.85,
    "EditorTabs.underlinedTabForeground": P.CANDLE_GOLD,
    "Debugger.Variables.valueForeground": P.COLD_STEEL_BRIGHT,
    "Debugger.Variables.collectingDataForeground": P.ASH,
    "Debugger.Variables.evaluatingExpressionForeground": P.ASH,
    "Debugger.Variables.changedValueForeground": P.CANDLE_GOLD,
    "Debugger.Variables.modifyingValueForeground": P.CANDLE_GOLD,
    "Debugger.Variables.errorMessageForeground": "text-error",
    "Debugger.Variables.exceptionForeground": "text-error",
    "Debugger.Variables.typeForeground": P.ASH,
    "FileColor.Yellow": "#2A2318", "FileColor.Green": "#22231A", "FileColor.Orange": "#2E2118",
    "FileColor.Rose": "#2E1D1B", "FileColor.Violet": "#2A2420", "FileColor.Blue": "#1F2423", "FileColor.Gray": "#211E1B",
    "UnattendedHostStatus.warningBackground": P.CANDLE_GOLD,
    "UnattendedHostStatus.warningForeground": P.OBSIDIAN,
    "UnattendedHostStatus.dangerBackground": P.EMBER_RED,
    "RunWidget.hoverBackground": P.VOID + "19",
    "RunWidget.pressedBackground": P.VOID + "28",
    "ToolWindow.Button.DragAndDrop.buttonDropBackground": P.BRONZE + "80",
    "ToolWindow.DragAndDrop.areaBackground": P.BRONZE + "4D",
    "DragAndDrop.rowBackground": P.OLD_GOLD + "26",
    "DragAndDrop.areaBackground": P.BRIGHT_PARCHMENT + "10",
    "VersionControl.GitLog.headIconColor": P.CANDLE_GOLD,
    "VersionControl.GitLog.localBranchIconColor": P.TYPE,
    "VersionControl.GitLog.remoteBranchIconColor": P.FADED_GOLD_BRIGHT,
    "VersionControl.GitLog.otherIconColor": P.OLD_PAPER,
    "VersionControl.GitLog.tagIconColor": P.OLD_PAPER,
    "VersionControl.Log.Commit.currentBranchBackground": "#2A2118",
    "VersionControl.Log.Commit.hoveredBackground": P.BRIGHT_PARCHMENT + "10",
    "VersionControl.FileHistory.Commit.selectedBranchBackground": "#2A2118",
    "VersionControl.Merge.Status.NoConflicts.foreground": P.TYPE,
    "MemoryIndicator.usedBackground": P.BRONZE + "80",
    "HelpBrowser.titleHighlightForeground": P.OLD_GOLD,
    "DataSummary.Chart.barColor": P.OLD_GOLD,
    "Editor.ToolTip.selectionBackground": P.SELECTED_IRON,
    "MainWindow.Tab.background": P.VOID,
    "Link.activeForeground": "text-link",
    "Link.hoverForeground": P.OLD_GOLD,
    "Link.pressedForeground": P.OLD_GOLD,
    "Link.visitedForeground": P.OLD_GOLD,
}
for i, (name, (a1, a1s, a2, bg, grad, av1, av2)) in enumerate(P.PROJECT_GRADIENTS.items(), start=1):
    UI_OVERRIDES[f"RecentProject.Color{i}.MainToolbarGradientStart"] = grad
    UI_OVERRIDES[f"RecentProject.Color{i}.Avatar.Start"] = av1
    UI_OVERRIDES[f"RecentProject.Color{i}.Avatar.End"] = av2


def remap_ui_literals(node):
    if isinstance(node, dict):
        return {k: remap_ui_literals(v) for k, v in node.items()}
    if isinstance(node, list):
        return [remap_ui_literals(v) for v in node]
    if isinstance(node, str) and node.startswith("#") and len(node) in (7, 9):
        return P.remap(node, P.UI_SOURCE_MAP)
    return node


def icon_palette():
    icons = json.loads((REF / "icon-colors.json").read_text(encoding="utf-8"))
    pal = {}
    for d in icons:
        src = d["color"]
        r, g, b, a = P.parse(src)
        key = f"{r:02X}{g:02X}{b:02X}"
        if key == "FFFFFF":
            target = P.to_hex(*P.parse(P.BRIGHT_PARCHMENT)[:3], a)
        elif key == "000000":
            target = P.to_hex(*P.parse(P.VOID)[:3], a)
        else:
            target = P.remap(src, P.ICON_SOURCE_MAP)
        for k in (src, src.upper(), src.lower()):
            pal[k] = target
    pal = dict(sorted(pal.items()))
    pal.update(P.ICON_NAMED_PALETTE)
    return pal


def build_theme():
    ref = json.loads((REF / "ManyIslandsDark.theme.json").read_text(encoding="utf-8"))
    colors = P.islands_colors()
    # safety net: any reference token we did not define keeps a materialised version of its value
    for name, val in ref["colors"].items():
        if name not in colors:
            colors[name] = P.remap(val, P.UI_SOURCE_MAP) if val.startswith("#") else val
    ui = remap_ui_literals(ref["ui"])
    for key, val in UI_OVERRIDES.items():
        set_ui(ui, key, val)
    theme = {
        "name": THEME_NAME,
        "dark": True,
        "author": AUTHOR,
        "parentTheme": ref.get("parentTheme", "ExperimentalDark"),
        "editorScheme": "/RiseCodex.xml",
        "colors": colors,
        "ui": ui,
        "icons": {"ColorPalette": icon_palette()},
    }
    out = SRC / "rise-codex.theme.json"
    out.write_text(json.dumps(theme, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return theme


# =============================================================================== scheme XML
def attr(fg=None, bg=None, effect=None, effect_type=None, stripe=None, font=None):
    d = {}
    if bg:
        d["BACKGROUND"] = bg
    if effect:
        d["EFFECT_COLOR"] = effect
    if effect_type is not None:
        d["EFFECT_TYPE"] = str(effect_type)
    if stripe:
        d["ERROR_STRIPE_COLOR"] = stripe
    if font is not None:
        d["FONT_TYPE"] = str(font)
    if fg:
        d["FOREGROUND"] = fg
    return d


def many(names, value):
    return {n: dict(value) for n in names}


ATTR_OVERRIDES = {}
ATTR_OVERRIDES.update({
    "TEXT": attr(fg=P.PARCHMENT, bg=P.OBSIDIAN),
    "DEFAULT_KEYWORD": attr(fg=P.KEYWORD, font=0),
    "ReSharper.NAMESPACE_IDENTIFIER": attr(fg=P.OLD_PAPER, font=0),
    "DEFAULT_PARAMETER": attr(fg=P.OLD_PAPER, font=0),
    "DEFAULT_REASSIGNED_PARAMETER": attr(fg=P.OLD_PAPER, effect=P.FADED_INK, effect_type=1, font=0),
    "DEFAULT_REASSIGNED_LOCAL_VARIABLE": attr(fg=P.PARCHMENT, effect=P.FADED_INK, effect_type=1, font=0),
    "DEFAULT_IDENTIFIER": attr(fg=P.PARCHMENT),
    "ReSharper.EVENT_IDENTIFIER": attr(fg=P.COPPER, font=0),
    "DEFAULT_CONSTANT": attr(fg=P.OLD_GOLD, font=0),
    "DEFAULT_LABEL": attr(fg=P.OLD_GOLD, font=1),
    "DEFAULT_PREDEFINED_SYMBOL": attr(fg=P.PARCHMENT),
    "DEFAULT_STRING": attr(fg=P.OLD_GOLD, font=0),
    "DEFAULT_VALID_STRING_ESCAPE": attr(fg=P.COPPER, font=0),
    "DEFAULT_INVALID_STRING_ESCAPE": attr(fg=P.OLD_GOLD, effect=P.EMBER_RED, effect_type=2, font=0),
    "ReSharper.MATCHED_FORMAT_STRING_ITEM": attr(bg=P.BORDER),
    "DEFAULT_NUMBER": attr(fg=P.COLD_STEEL, font=0),
    "DEFAULT_METADATA": attr(fg=P.COPPER, font=0),
    "DEFAULT_DOC_COMMENT": attr(fg=P.FADED_GOLD, font=0),
    "DEFAULT_DOC_COMMENT_TAG": attr(fg=P.OLD_PAPER),
    "DEFAULT_DOC_COMMENT_TAG_VALUE": attr(fg=P.OLD_PAPER),
    "DEFAULT_DOC_MARKUP": attr(fg=P.FADED_GOLD),
    "DEFAULT_TAG": attr(fg=P.TYPE, font=0),
    "DEFAULT_ATTRIBUTE": attr(fg=P.OLD_PAPER),
    "DEFAULT_ENTITY": attr(fg=P.COPPER, font=0),
    "XML_ATTRIBUTE_NAME": attr(fg=P.OLD_PAPER),
    "HTML_ATTRIBUTE_NAME": attr(fg=P.OLD_PAPER),
    "XML_ENTITY_REFERENCE": attr(fg=P.COPPER, font=0),
    "HTML_ENTITY_REFERENCE": attr(fg=P.COPPER, font=0),
    "XML_CUSTOM_TAG_NAME": attr(fg=P.TYPE, font=0),
    "XML_TAG_DATA": attr(fg=P.PARCHMENT),
    "JSON.PROPERTY_KEY": attr(fg=P.PARCHMENT),
    "YAML_SCALAR_KEY": attr(fg=P.PARCHMENT, font=0),
    "YAML_SIGN": attr(fg=P.OLD_PAPER, font=0),
    "YAML_ANCHOR": attr(fg=P.COLD_STEEL),
    "MARKDOWN_BOLD": attr(font=1),
    "MARKDOWN_ITALIC": attr(font=2),
    "MARKDOWN_LINK_TEXT": attr(fg=P.CANDLE_GOLD),
    "MARKDOWN_LINK_DESTINATION": attr(fg=P.OLD_PAPER, effect=P.LINK_UNDERLINE, effect_type=1),
    "MARKDOWN_AUTO_LINK": attr(fg=P.CANDLE_GOLD, effect=P.LINK_UNDERLINE, effect_type=1),
    "MARKDOWN_BLOCK_QUOTE": attr(fg=P.ASH),
    "MARKDOWN_LIST_MARKER": attr(fg=P.COPPER),
    "MARKDOWN_HRULE": attr(fg=P.ASH, font=0),
    "MARKDOWN_TABLE_SEPARATOR": attr(fg=P.ASH, font=0),
    "MARKDOWN_HTML_BLOCK": attr(fg=P.PARCHMENT),
    # errors / warnings
    "ERRORS_ATTRIBUTES": attr(bg=P.EMBER_RED, fg=P.BRIGHT_PARCHMENT, stripe=P.EMBER_RED),  # whole word on ember, like a breakpoint line
    "WARNING_ATTRIBUTES": attr(effect=P.CANDLE_GOLD, effect_type=2, stripe=P.OLD_GOLD),
    "WEAK_WARNING_ATTRIBUTES": attr(effect=P.FADED_GOLD, effect_type=2, stripe=P.FADED_GOLD),
    "INFO_ATTRIBUTES": attr(effect=P.FADED_INK, effect_type=2, stripe=P.FADED_INK),
    "TYPO": attr(effect=P.OXIDIZED_BRASS, effect_type=2),
    "GRAMMAR_ERROR": attr(effect=P.FADED_GOLD, effect_type=2),
    "SUGGESTION": attr(effect=P.FADED_INK, effect_type=2, stripe=P.FADED_INK),
    "NOT_USED_ELEMENT_ATTRIBUTES": attr(fg=P.ASH),
    "DEPRECATED_ATTRIBUTES": attr(effect=P.OLD_PAPER, effect_type=3),
    "MARKED_FOR_REMOVAL_ATTRIBUTES": attr(effect=P.EMBER_RED, effect_type=3),
    "WRONG_REFERENCES_ATTRIBUTES": attr(bg=P.EMBER_RED, fg=P.BRIGHT_PARCHMENT, stripe=P.EMBER_RED, font=0),
    "RUNTIME_ERROR": attr(bg=P.EMBER_RED, fg=P.BRIGHT_PARCHMENT, stripe=P.EMBER_RED),
    "GENERIC_SERVER_ERROR_OR_WARNING": attr(effect=P.OLD_GOLD, effect_type=1, stripe=P.OLD_GOLD),
    "DUPLICATE_FROM_SERVER": attr(bg=P.WARNING_SECONDARY_BG),
    "DELETED_TEXT_ATTRIBUTES": attr(fg=P.PARCHMENT, effect=P.EMBER_RED, effect_type=3),
    "TEXT_STYLE_ERROR": attr(effect=P.EMBER_RED, effect_type=2),
    "TEXT_STYLE_WARNING": attr(effect=P.CANDLE_GOLD, effect_type=2),
    "TEXT_STYLE_SUGGESTION": attr(effect=P.FADED_INK, effect_type=2),
    # editor highlights
    "CARET_ROW": attr(bg=P.CARET_ROW),
    "IDENTIFIER_UNDER_CARET_ATTRIBUTES": attr(bg=P.SELECTED_IRON, effect_type=0, stripe=P.BORDER),
    "WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES": attr(bg=P.USAGE_WRITE_BG, effect_type=0, stripe=P.BRONZE),
    "SEARCH_RESULT_ATTRIBUTES": attr(bg=P.SEARCH_BG, fg=P.SEARCH_FG, stripe=P.BRONZE),
    "TEXT_SEARCH_RESULT_ATTRIBUTES": attr(bg=P.SEARCH_BG, fg=P.SEARCH_FG, stripe=P.BRONZE),
    "WRITE_SEARCH_RESULT_ATTRIBUTES": attr(bg=P.SEARCH_BG, fg=P.SEARCH_FG, stripe=P.OLD_GOLD),
    "MATCHED_BRACE_ATTRIBUTES": attr(bg=P.BORDER, fg=P.CANDLE_GOLD, effect_type=0, font=1),
    "UNMATCHED_BRACE_ATTRIBUTES": attr(bg=P.BREAKPOINT_LINE, fg=P.EMBER_BRIGHT, effect=P.WAX_RED, effect_type=0, font=1),
    "FOLDED_TEXT_ATTRIBUTES": attr(bg=P.TAB_INACTIVE_BG, fg=P.OLD_PAPER, effect=P.BORDER),
    "TODO_DEFAULT_ATTRIBUTES": attr(fg=P.CANDLE_GOLD, font=1, stripe=P.OLD_GOLD),
    "BOOKMARKS_ATTRIBUTES": attr(stripe=P.OLD_GOLD),
    "BREAKPOINT_ATTRIBUTES": attr(bg=P.BREAKPOINT_LINE),
    "EXECUTIONPOINT_ATTRIBUTES": attr(bg=P.EXEC_POINT, font=1),
    "DEBUGGER_INLINED_VALUES": attr(fg=P.COLD_STEEL, font=2),
    "DEBUGGER_INLINED_VALUES_MODIFIED": attr(fg=P.COPPER, font=2),
    "DEBUGGER_INLINED_VALUES_EXECUTION_LINE": attr(fg=P.COLD_STEEL_BRIGHT, font=2),
    "DEBUGGER_PREDICTED_VALUE_TRUE": attr(bg=P.SUCCESS_SECONDARY_BG),
    "DEBUGGER_PREDICTED_VALUE_TRUE_ALT": attr(bg=P.SUCCESS_SECONDARY_BG),
    "DEBUGGER_PREDICTED_VALUE_FALSE": attr(bg=P.BREAKPOINT_LINE),
    "DEBUGGER_PREDICTED_VALUE_FALSE_ALT": attr(bg=P.BREAKPOINT_LINE),
    "DEBUGGER_PREDICTED_FLOW": attr(effect=P.FADED_GOLD, effect_type=0),
    "DEBUGGER_PREDICTED_EXCEPTION": attr(effect=P.FADED_GOLD, effect_type=2),
    "DEBUGGER_PREDICTED_SCOPE": attr(effect=P.AI_BORDER, effect_type=0),
    "DEBUGGER_UNREACHABLE_DECORATION": attr(fg=P.ASH, effect=P.FADED_INK, effect_type=3),
    "INLINE_PARAMETER_HINT": attr(bg=P.RAISED_IRON, fg=P.ASH, font=0),
    "INLINE_PARAMETER_HINT_CURRENT": attr(bg=P.SELECTED_IRON, fg=P.OLD_PAPER, font=0),
    "INLINE_PARAMETER_HINT_HIGHLIGHTED": attr(bg=P.USAGE_WRITE_BG, fg=P.PARCHMENT),
    "CODE_VISION_DEFAULT": attr(fg=P.ASH, font=0),
    "CODE_VISION_HOVERED": attr(fg=P.CANDLE_GOLD, font=0),
    "HYPERLINK_ATTRIBUTES": attr(fg=P.CANDLE_GOLD, effect=P.LINK_UNDERLINE, effect_type=1),
    "FOLLOWED_HYPERLINK_ATTRIBUTES": attr(fg=P.OLD_GOLD, effect=P.LINK_UNDERLINE, effect_type=1),
    "INACTIVE_HYPERLINK_ATTRIBUTES": attr(fg=P.OLD_PAPER, effect=P.FADED_INK, effect_type=1),
    "CTRL_CLICKABLE": attr(fg=P.CANDLE_GOLD, effect=P.CANDLE_GOLD, effect_type=1),
    "LIVE_TEMPLATE_ATTRIBUTES": attr(effect=P.BRONZE),
    "LIVE_TEMPLATE_INACTIVE_SEGMENT": attr(effect=P.FADED_INK),
    "TEMPLATE_VARIABLE_ATTRIBUTES": attr(fg=P.COPPER, font=0),
    "INJECTED_LANGUAGE_FRAGMENT": attr(bg=P.INJECTED_BG),
    "DEFAULT_TEMPLATE_LANGUAGE_COLOR": attr(bg=P.INJECTED_BG),
    "ReSharper.CONTEXT_EXIT": attr(bg=P.USAGE_WRITE_BG, stripe=P.USAGE_WRITE_BG),
    "ReSharper.NAME_OR_SIGNATURE_CHANGED": attr(bg=P.SELECTED_IRON),
    "ReSharper.REARRANGE_LEFT_RIGHT_CODE_HINT": attr(bg=P.SELECTED_IRON),
    "ReSharper.REARRANGE_UP_DOWN_CODE_HINT": attr(bg="#22201A"),
    "ReSharper.BRACE_OUTLINE": attr(effect=P.BRONZE),
    "ReSharper.HINT": attr(effect=P.ASH, effect_type=5),
    "ReSharper.INACTIVE_PREPROCESSOR_BRANCH": attr(fg=P.FADED_INK),
    "ReSharper.LATE_BOUND_IDENTIFIER": attr(fg=P.ASH, font=1),
    "ReSharper.ST_SUSPICIOUS_TEXT": attr(effect=P.CANDLE_GOLD, effect_type=2),
    "ReSharper.UNITY_PERFORMANCE_COSTLY_METHOD_HIGHLIGHTER": attr(bg="#3A2A1F"),
    "ReSharper.ReSharper.ShaderLab_ENABLED_SHADER_KEYWORD": attr(fg=P.TYPE, font=1, effect=P.TYPE, effect_type=1),
    "ReSharper.ReSharper.ShaderLab_IMPLICITLY_ENABLED_SHADER_KEYWORD": attr(fg=P.TYPE, font=1),
    "ReSharper.ReSharper.ShaderLab_DISABLED_SHADER_KEYWORD": attr(fg=P.ASH),
    "ReSharper.ReSharper.ShaderLab_SUPPRESSED_SHADER_KEYWORD": attr(fg=P.ASH, effect=P.ASH, effect_type=3),
    "ReSharper.CPP_ENUM_ENUMERATOR_IDENTIFIER": attr(fg=P.OLD_GOLD, font=0),
    "ReSharper.CPP_LOCAL_TYPEDEF_IDENTIFIER": attr(fg=P.TYPE, font=0),
    "ReSharper.CPP_PREPROCESSOR_MACRO_IDENTIFIER": attr(fg=P.COPPER, font=0),
    "ReSharper.CPP_UE4_REFLECTION_SPECIFIER_IDENTIFIER": attr(fg=P.COPPER, font=0),
    "ReSharper.CPP_OVERLOADED_OPERATOR_IDENTIFIER": attr(fg=P.CANDLE_GOLD, font=0),
    "ReSharper.JS_XML_DOCUMENTATION_COMMENT": attr(fg=P.FADED_GOLD, font=0),
    "ReSharper.JSDOC_KEYWORD": attr(fg=P.OLD_PAPER, font=0),
    "ReSharper.JSDOC_PARAMETER_OR_PROPERTY_IDENTIFIER": attr(fg=P.OLD_PAPER),
    # console / terminal
    "CONSOLE_NORMAL_OUTPUT": attr(fg=P.PARCHMENT),
    "CONSOLE_SYSTEM_OUTPUT": attr(fg=P.OLD_PAPER),
    "CONSOLE_ERROR_OUTPUT": attr(fg=P.EMBER_BRIGHT),
    "CONSOLE_USER_INPUT": attr(fg=P.BRIGHT_PARCHMENT, font=0),
    "CONSOLE_PARAMETER": attr(fg=P.OLD_PAPER, font=0),
    "CONSOLE_SELECTED_PARAMETER": attr(bg="#4A3820", effect=P.OLD_GOLD, stripe="#4A3820"),
    "CONSOLE_RANGE_TO_EXECUTE": attr(effect=P.BRONZE),
    "CONSOLE_BLACK_OUTPUT": attr(fg=P.IRON),
    "CONSOLE_RED_OUTPUT": attr(fg=P.EMBER_RED),
    "CONSOLE_GREEN_OUTPUT": attr(fg=P.OXIDIZED_BRASS),
    "CONSOLE_YELLOW_OUTPUT": attr(fg=P.OLD_GOLD),
    "CONSOLE_BLUE_OUTPUT": attr(fg=P.COLD_STEEL),
    "CONSOLE_MAGENTA_OUTPUT": attr(fg=P.FADED_GOLD),
    "CONSOLE_CYAN_OUTPUT": attr(fg=P.CYAN_SUB),
    "CONSOLE_GRAY_OUTPUT": attr(fg=P.PARCHMENT),
    "CONSOLE_DARKGRAY_OUTPUT": attr(fg=P.FADED_INK),
    "CONSOLE_RED_BRIGHT_OUTPUT": attr(fg=P.EMBER_BRIGHT),
    "CONSOLE_GREEN_BRIGHT_OUTPUT": attr(fg=P.BRASS_BRIGHT),
    "CONSOLE_YELLOW_BRIGHT_OUTPUT": attr(fg=P.CANDLE_GOLD),
    "CONSOLE_BLUE_BRIGHT_OUTPUT": attr(fg=P.COLD_STEEL_BRIGHT),
    "CONSOLE_MAGENTA_BRIGHT_OUTPUT": attr(fg=P.FADED_GOLD_BRIGHT),
    "CONSOLE_CYAN_BRIGHT_OUTPUT": attr(fg=P.CYAN_BRIGHT),
    "CONSOLE_WHITE_OUTPUT": attr(fg=P.BRIGHT_PARCHMENT),
    "LOG_ERROR_OUTPUT": attr(fg=P.EMBER_BRIGHT, font=1),
    "LOG_WARNING_OUTPUT": attr(fg=P.CANDLE_GOLD),
    "LOG_INFO_OUTPUT": attr(fg=P.OLD_PAPER),
    "LOG_DEBUG_OUTPUT": attr(fg=P.ASH),
    "LOG_VERBOSE_OUTPUT": attr(fg=P.FADED_INK),
    "LOG_EXPIRED_ENTRY": attr(fg=P.FADED_INK),
    "TERMINAL_COMMAND_TO_RUN_USING_IDE": attr(bg=P.SELECTED_IRON),
    # diff / vcs / coverage
    "DIFF_INSERTED": attr(bg=P.DIFF_INSERTED, stripe=P.GUTTER_ADDED),
    "DIFF_DELETED": attr(bg=P.DIFF_DELETED, stripe=P.WAX_RED),
    "DIFF_MODIFIED": attr(bg=P.DIFF_MODIFIED, stripe=P.BRONZE),
    "DIFF_CONFLICT": attr(bg=P.DIFF_CONFLICT, stripe=P.EMBER_RED),
    "LINE_FULL_COVERAGE": attr(bg="#22231A"),
    "LINE_PARTIAL_COVERAGE": attr(bg=P.WARNING_SECONDARY_BG),
    "LINE_NONE_COVERAGE": attr(bg=P.BREAKPOINT_LINE),
    "BREADCRUMBS_DEFAULT": attr(bg=P.OBSIDIAN, fg=P.OLD_PAPER),
    "BREADCRUMBS_CURRENT": attr(bg=P.SELECTED_IRON, fg=P.PARCHMENT),
    "BREADCRUMBS_HOVERED": attr(bg=P.RAISED_IRON, fg=P.PARCHMENT),
    "BREADCRUMBS_INACTIVE": attr(bg=P.OBSIDIAN, fg=P.ASH),
})
ATTR_OVERRIDES.update(many(["DEFAULT_CLASS_NAME", "DEFAULT_INTERFACE_NAME", "DEFAULT_CLASS_REFERENCE",
                            "ReSharper.STRUCT_IDENTIFIER", "ReSharper.ENUM_IDENTIFIER", "ReSharper.DELEGATE_IDENTIFIER",
                            "ReSharper.STATIC_CLASS_IDENTIFIER", "ReSharper.TYPE_PARAMETER_IDENTIFIER", "ReSharper.ST_TYPE"],
                           attr(fg=P.TYPE, font=0)))
ATTR_OVERRIDES.update(many(["DEFAULT_FUNCTION_DECLARATION", "DEFAULT_FUNCTION_CALL", "DEFAULT_INSTANCE_METHOD",
                            "DEFAULT_STATIC_METHOD", "ReSharper.EXTENSION_METHOD_IDENTIFIER", "ReSharper.ST_METHOD"],
                           attr(fg=P.CANDLE_GOLD, font=0)))
ATTR_OVERRIDES.update(many(["DEFAULT_LOCAL_VARIABLE", "ReSharper.MUTABLE_LOCAL_VARIABLE_IDENTIFIER", "DEFAULT_GLOBAL_VARIABLE",
                            "DEFAULT_INSTANCE_FIELD", "DEFAULT_STATIC_FIELD",
                            "ReSharper.CPP_STRUCT_FIELD_IDENTIFIER", "ReSharper.CPP_UNION_MEMBER_IDENTIFIER",
                            "ReSharper.CPP_GLOBAL_VARIABLE_IDENTIFIER", "ReSharper.CPP_LOCAL_VARIABLE_IDENTIFIER",
                            "ReSharper.CPP_DEPENDENT_NAME_IDENTIFIER"],
                           attr(fg=P.PARCHMENT, font=0)))
ATTR_OVERRIDES.update(many(["ReSharper.STRING_ESCAPE_CHARACTER_2", "ReSharper.FORMAT_STRING_ITEM", "ReSharper.FORMAT_STRING_ITEM_2"],
                           attr(fg=P.COPPER, font=0)))
ATTR_OVERRIDES.update(many(["DEFAULT_LINE_COMMENT", "DEFAULT_BLOCK_COMMENT"], attr(fg=P.ASH, font=0)))
ATTR_OVERRIDES.update(many(["DEFAULT_OPERATION_SIGN", "DEFAULT_BRACES", "DEFAULT_BRACKETS", "DEFAULT_PARENTHS",
                            "DEFAULT_COMMA", "DEFAULT_SEMICOLON", "DEFAULT_DOT"], attr(fg=P.OLD_PAPER, font=0)))
ATTR_OVERRIDES.update(many([f"MARKDOWN_HEADER_LEVEL_{i}" for i in range(1, 7)], attr(fg=P.OLD_GOLD, font=1)))
ATTR_OVERRIDES.update(many(["MARKDOWN_CODE_SPAN", "MARKDOWN_CODE_BLOCK", "MARKDOWN_CODE_FENCE"], attr(fg=P.COLD_STEEL, font=0)))
ATTR_OVERRIDES.update(many(["ReSharper.PATH_IDENTIFIER", "ReSharper.ST_HYPERLINK", "ReSharper.ST_PATH", "CSS.URL"],
                           attr(fg=P.CANDLE_GOLD, effect=P.LINK_UNDERLINE, effect_type=1)))
ATTR_OVERRIDES.update(many(["ReSharper.UNITY_PERFORMANCE_CAMERA_MAIN", "ReSharper.UNITY_PERFORMANCE_COSTLY_METHOD_INVOCATION",
                            "ReSharper.UNITY_PERFORMANCE_NULL_COMPARISON"], attr(effect=P.COPPER, effect_type=1)))
ATTR_OVERRIDES.update(many(["ReSharper.JS_PROPERTY_IDENTIFIER", "ReSharper.JS_UNKNOWN_PROPERTY_IDENTIFIER"], attr(fg=P.PARCHMENT)))

COLOR_OVERRIDES = {
    "CARET_COLOR": P.CANDLE_GOLD,
    "CARET_ROW_COLOR": P.CARET_ROW,
    "SELECTION_BACKGROUND": P.SELECTION,
    "SELECTION_FOREGROUND": "",
    "LINE_NUMBERS_COLOR": P.FADED_INK,
    "LINE_NUMBER_ON_CARET_ROW_COLOR": P.OLD_GOLD,
    "GUTTER_BACKGROUND": P.OBSIDIAN,
    "INDENT_GUIDE": P.GUIDE,
    "SELECTED_INDENT_GUIDE": "#4A3A28",
    "RIGHT_MARGIN_COLOR": P.SELECTED_IRON,
    "WHITESPACES": P.BORDER,
    "TEARLINE_COLOR": P.BORDER,
    "SELECTED_TEARLINE_COLOR": P.BRONZE,
    "CONSOLE_BACKGROUND_KEY": P.VOID,
    "DOCUMENTATION_COLOR": P.IRON,
    "LOOKUP_COLOR": P.IRON,
    "NOTIFICATION_BACKGROUND": P.RAISED_IRON,
    "ERROR_HINT": P.ERROR_SECONDARY_BG,
    "INFORMATION_HINT": P.RAISED_IRON,
    "QUESTION_HINT": "#2E2620",
    "ADDED_LINES_COLOR": P.GUTTER_ADDED,
    "MODIFIED_LINES_COLOR": P.BRONZE,
    "DELETED_LINES_COLOR": P.WAX_RED,
    "WHITESPACES_MODIFIED_LINES_COLOR": P.SEARCH_BG,
    "DIFF_SEPARATORS_BACKGROUND": P.BORDER,
    "METHOD_SEPARATORS_COLOR": P.SOFT_BORDER,
    "FOLDED_TEXT_BORDER_COLOR": P.BORDER,
    "ANNOTATIONS_COLOR": P.ASH,
    "VCS_ANNOTATIONS_COLOR_1": "#1A1512",
    "VCS_ANNOTATIONS_COLOR_2": "#1E1814",
    "VCS_ANNOTATIONS_COLOR_3": "#221B16",
    "VCS_ANNOTATIONS_COLOR_4": "#261E18",
    "VCS_ANNOTATIONS_COLOR_5": P.SELECTED_IRON,
    "READONLY_BACKGROUND": P.INJECTED_BG,
    "READONLY_FRAGMENT_BACKGROUND": P.TAB_INACTIVE_BG,
    "RECURSIVE_CALL_ATTRIBUTES": P.COPPER,
    "SOFT_WRAP_SIGN_COLOR": P.FADED_INK,
    "BookmarkIcon.background": P.OLD_GOLD,
    "MnemonicIcon.background": P.OLD_GOLD,
    "MnemonicIcon.borderColor": P.IRON,
    "MnemonicIcon.foreground": P.OBSIDIAN,
    "HTML_TAG_TREE_LEVEL0": P.RUST,
    "HTML_TAG_TREE_LEVEL1": P.OLD_GOLD,
    "HTML_TAG_TREE_LEVEL2": P.OXIDIZED_BRASS,
    "HTML_TAG_TREE_LEVEL3": P.COLD_STEEL,
    "HTML_TAG_TREE_LEVEL4": P.BRONZE,
    "HTML_TAG_TREE_LEVEL5": P.FADED_GOLD,
    "ScrollBar.background": P.IRON,
}
for prefix in ("ScrollBar.", "ScrollBar.Transparent.", "ScrollBar.Mac.", "ScrollBar.Mac.Transparent."):
    transparent_track = prefix != "ScrollBar." and prefix != "ScrollBar.Mac."
    COLOR_OVERRIDES[prefix + "thumbColor"] = P.BRONZE + "66"
    COLOR_OVERRIDES[prefix + "thumbBorderColor"] = P.BRONZE + "66"
    COLOR_OVERRIDES[prefix + "hoverThumbColor"] = P.BRONZE + "B3"
    COLOR_OVERRIDES[prefix + "hoverThumbBorderColor"] = P.BRONZE + "B3"
    COLOR_OVERRIDES[prefix + "trackColor"] = (P.IRON + "00") if transparent_track else P.OBSIDIAN
    COLOR_OVERRIDES[prefix + "hoverTrackColor"] = (P.IRON + "00") if transparent_track else P.OBSIDIAN

COLOR_KEYS = ("FOREGROUND", "BACKGROUND", "EFFECT_COLOR", "ERROR_STRIPE_COLOR")


def scheme_hex(value):
    """'#RRGGBB[AA]' -> 'RRGGBB[AA]' (IntelliJ scheme format)."""
    return value.lstrip("#").upper()


def build_scheme():
    tree = ET.parse(REF / "RiderIslandsDark.xml")
    root = tree.getroot()
    root.set("name", SCHEME_NAME)
    root.set("parent_scheme", "Darcula")
    root.set("version", "142")
    # fonts (before <colors>)
    for i, (name, val) in enumerate(FONT_OPTIONS):
        el = ET.Element("option")
        el.set("name", name)
        el.set("value", val)
        root.insert(i, el)
    # colours
    colors = root.find("colors")
    for opt in colors.findall("option"):
        v = opt.get("value")
        if v:
            opt.set("value", scheme_hex(P.remap(v, P.SCHEME_SOURCE_MAP)))
    existing = {opt.get("name"): opt for opt in colors.findall("option")}
    for name, val in COLOR_OVERRIDES.items():
        el = existing.get(name)
        if el is None:
            el = ET.SubElement(colors, "option")
            el.set("name", name)
        el.set("value", scheme_hex(val) if val else "")
    # attributes
    attrs = root.find("attributes")
    for opt in attrs.findall("option"):
        val = opt.find("value")
        if val is None:
            continue
        for o in val.findall("option"):
            if o.get("name") in COLOR_KEYS and o.get("value"):
                o.set("value", scheme_hex(P.remap(o.get("value"), P.SCHEME_SOURCE_MAP)))
    existing = {opt.get("name"): opt for opt in attrs.findall("option")}
    for name, spec in ATTR_OVERRIDES.items():
        el = existing.get(name)
        if el is None:
            el = ET.SubElement(attrs, "option")
            el.set("name", name)
        if "baseAttributes" in el.attrib:
            del el.attrib["baseAttributes"]
        for child in list(el):
            el.remove(child)
        val = ET.SubElement(el, "value")
        for k in sorted(spec):
            o = ET.SubElement(val, "option")
            o.set("name", k)
            o.set("value", scheme_hex(spec[k]) if k in COLOR_KEYS else spec[k])
    # sort attributes by name for stable diffs
    sorted_opts = sorted(attrs.findall("option"), key=lambda e: e.get("name"))
    for e in list(attrs):
        attrs.remove(e)
    for e in sorted_opts:
        attrs.append(e)
    sorted_cols = sorted(colors.findall("option"), key=lambda e: e.get("name"))
    for e in list(colors):
        colors.remove(e)
    for e in sorted_cols:
        colors.append(e)
    ET.indent(tree, space="  ")
    out = SRC / "RiseCodex.xml"
    out.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    return root


def main():
    theme = build_theme()
    root = build_scheme()
    n_attrs = len(root.find("attributes").findall("option"))
    n_cols = len(root.find("colors").findall("option"))
    print(f"theme.json: {len(theme['colors'])} colours, {len(theme['icons']['ColorPalette'])} icon palette entries")
    print(f"RiseCodex.xml: {n_attrs} attributes, {n_cols} colours")


if __name__ == "__main__":
    main()
