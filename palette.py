"""Rise / Codex palette - single source of truth.

Spec tokens come from rise_codex_ide_theme_spec.md; amendments (accepted by the user) are marked.
All values are '#RRGGBB'. Ramps mirror the Islands Dark token ramps (10..160) so the Islands
`ui` section can be reused unchanged; each ramp is re-materialised into a spec material.
"""
import colorsys

# ---- text lift (v1.0.1) --------------------------------------------------------
# After the first in-IDE review the user asked for slightly lighter, slightly more saturated text
# ("halfway between the HTML mock and the IDE"). TEXT_LIFT = 0 reproduces the spec values,
# 1 is the full lift (+10 % lightness, x1.25 saturation); 0.5 is the agreed halfway point.
# Only foreground/text tokens are lifted; backgrounds, borders and accent fills stay as specified.
TEXT_LIFT = 0.5


def lift(hexstr, k=None, dl=0.10, ds=0.25):
    """Lighten (+dl*k in HLS lightness) and saturate (x(1+ds*k)) a '#RRGGBB' colour."""
    k = TEXT_LIFT if k is None else k
    if k == 0:
        return hexstr
    v = int(hexstr.lstrip("#"), 16)
    r, g, b = (v >> 16) & 255, (v >> 8) & 255, v & 255
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    l = min(1.0, l + dl * k)
    s = min(1.0, s * (1 + ds * k))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


# ---- spec tokens -------------------------------------------------------------
VOID = "#0B0908"
OBSIDIAN = "#110E0C"
IRON = "#181310"
RAISED_IRON = "#211A15"
SELECTED_IRON = "#2A211A"      # spec "Selected Item"
BORDER = "#3B2D22"
BRONZE = "#6E5033"
OLD_GOLD = lift("#A37843")
CANDLE_GOLD = lift("#C09152")
PARCHMENT = lift("#C7AE87")
OLD_PAPER = lift("#9E8768")
ASH = lift("#75685A")
FADED_INK = "#50463C"
RUST = "#9A5635"
COPPER = lift("#B87545")
WAX_RED = "#783A32"
EMBER_RED = "#A14D3E"
OXIDIZED_BRASS = "#77704E"
COLD_STEEL = lift("#748080")
# spec values that had no token name
FADED_GOLD = lift("#806C50")         # doc comments
GUIDE = "#30271F"                    # indent guides
SELECTION = "#49331F"
SEARCH_BG = "#5A3C20"
SEARCH_FG = lift("#D2B47C")
BRIGHT_PARCHMENT = lift("#D5C3A5", dl=0.05)   # terminal bright white
EMBER_BRIGHT = lift("#B75A49")       # terminal bright red / error text (amendment 3)
BRASS_BRIGHT = lift("#91916A")
FADED_GOLD_BRIGHT = lift("#9A7D5D")
COLD_STEEL_BRIGHT = lift("#8C9999")
CYAN_SUB = lift("#7E9489")           # spec #7F8580 nudged greener so it differs from BLUE (#748080)
CYAN_BRIGHT = lift("#9AA3A0")
# ---- amendments --------------------------------------------------------------
KEYWORD = lift("#B9663D")            # lit rust, 4.6:1 before lift (spec #9A5635 is 3.4:1 on the editor bg)
TYPE = lift("#8E8663")               # lifted oxidized brass (spec #77704E is 3.9:1)
ERROR_TEXT = EMBER_BRIGHT
# ---- derived -----------------------------------------------------------------
CARET_ROW = "#171210"
SOFT_BORDER = "#2C221A"
TAB_INACTIVE_BG = "#1A1512"
INLINE_BG = "#1C1612"
INJECTED_BG = "#151110"
BRAND_SECONDARY_BG = "#3A2A1C"
BRAND_SECONDARY_BORDER = "#4E3823"
ERROR_SECONDARY_BG = "#3A211D"
ERROR_SECONDARY_BORDER = "#5E332B"
WARNING_SECONDARY_BG = "#3D2E18"
WARNING_SECONDARY_BORDER = "#5A4426"
SUCCESS_SECONDARY_BG = "#2E2C1F"
SUCCESS_SECONDARY_BORDER = "#474428"
SUCCESS_HOVER = "#6A6545"
AI_BG = "#2B241B"
AI_BORDER = "#4E3F2A"
DIFF_INSERTED = "#2A2B1C"
DIFF_DELETED = "#2E1B18"
DIFF_MODIFIED = "#2E2418"
DIFF_CONFLICT = "#3A211D"
GUTTER_ADDED = "#4A4A2E"
EXEC_POINT = "#4A3418"
BREAKPOINT_LINE = "#3A211D"
USAGE_WRITE_BG = "#33261B"
LINK_UNDERLINE = "#8A6338"
ICON_STROKE = lift("#B09A7A")

# ---- ramps (Islands token names -> materials) --------------------------------
RAMPS = {
    "gray":   ["#110E0C", "#181310", "#211A15", "#2A211A", "#3B2D22", "#50463C", "#5E5246", "#75685A",
               "#877866", "#9E8768", "#B09A7A", "#B8A180", "#C7AE87", "#D0BA98", "#D5C3A5", "#E3D4BC"],
    "blue":   ["#1B1611", "#221A12", "#2A2015", "#3A2A1C", "#49331F", "#5A3E25", "#644728", "#6E5033",
               "#8A6338", "#A37843", "#C09152", "#C9A268", "#D2B47C", "#DAC08F", "#E3CFA6", "#EEE1C9"],
    "green":  ["#15140F", "#1B1A12", "#22211A", "#2E2C1F", "#383621", "#474428", "#6A6545", "#77704E",
               "#8E8663", "#91916A", "#9E9C76", "#ABA985", "#B8B594", "#C5C2A5", "#D3D0B8", "#E4E1CE"],
    "red":    ["#1E120F", "#2A1816", "#33201C", "#3A211D", "#4F2A25", "#5E332B", "#783A32", "#A14D3E",
               "#B75A49", "#C4664F", "#CF7760", "#D88A74", "#E09C88", "#E8AF9F", "#F0C6B9", "#F7E0D8"],
    "yellow": ["#1C1710", "#241C12", "#2E2316", "#3D2E18", "#4A3820", "#5A4426", "#7A5A33", "#A37843",
               "#B08447", "#C09152", "#C99E62", "#D2AB74", "#DAB98A", "#E2C7A0", "#EAD5B8", "#F3E6D3"],
    "orange": ["#1E130E", "#261811", "#2F1D14", "#3E2718", "#4B2F1D", "#5F3B23", "#7E4D2D", "#9A5635",
               "#B87545", "#C4875A", "#CE976C", "#D7A67F", "#DFB593", "#E7C4A7", "#EFD5BD", "#F7E7D9"],
    "purple": ["#1B1712", "#2B241B", "#33291F", "#3E3225", "#4E3F2A", "#5B4A32", "#6B583C", "#806C50",
               "#8E7A5A", "#9A7D5D", "#A98D6E", "#B59C80", "#C1AB92", "#CDBAA4", "#DACAB8", "#E9DFD2"],
    "teal":   ["#131515", "#191C1C", "#212525", "#2A2F2F", "#343A3A", "#404747", "#4F5757", "#5F6969",
               "#6A7575", "#748080", "#8C9999", "#9AA3A0", "#A8B0AE", "#B7BDBB", "#C8CCCA", "#DEE0DF"],
}
STEPS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]


def ramp_tokens():
    out = {}
    for name, ramp in RAMPS.items():
        for step, hexv in zip(STEPS, ramp):
            out[f"{name}-{step}"] = hexv
    return out


# 9 warm project-colour families (welcome screen / toolbar project widget)
PROJECT_GRADIENTS = {
    # name: (a1, a1-secondary, a2, bg, toolbarGradientStart, avatarStart, avatarEnd)
    "g1-amber":  ("#6E3F2E", "#2E1F1A", "#36241C", "#241A15", "#5E3F2C", "#B87545", "#C4875A"),
    "g2-rust":   ("#6A4A22", "#2A2112", "#33291A", "#221C12", "#5A4426", "#A37843", "#B08447"),
    "g3-olive":  ("#55532A", "#22221A", "#2B2A1C", "#1E1E16", "#4A4A2E", "#8E8663", "#91916A"),
    "g4-sky":    ("#3B332C", "#1E1A17", "#2A2420", "#1C1816", "#3B332C", "#5E5246", "#75685A"),
    "g5-cobalt": ("#6E5033", "#2A2118", "#33291F", "#221B15", "#4E3823", "#6E5033", "#8A6338"),
    "g6-plum":   ("#6E3A33", "#2A1D1B", "#34231F", "#231B19", "#4F2A25", "#A14D3E", "#B75A49"),
    "g7-violet": ("#6B583C", "#27221B", "#322B21", "#221E18", "#4E3F2A", "#806C50", "#9A7D5D"),
    "g8-ocean":  ("#44514F", "#1E2322", "#262C2B", "#1B1F1F", "#34403F", "#748080", "#8C9999"),
    "g9-grass":  ("#5C5A3A", "#24231A", "#2D2C1F", "#1F1E17", "#383621", "#77704E", "#8E8663"),
}


def islands_colors():
    """Complete replacement for the `colors` block of ManyIslandsDark.theme.json."""
    c = {"white": "#E3D4BC", "black": VOID}
    c.update(ramp_tokens())
    c.update({
        "transparent-white-10": BRIGHT_PARCHMENT + "10", "transparent-white-20": BRIGHT_PARCHMENT + "17",
        "transparent-white-30": BRIGHT_PARCHMENT + "21", "transparent-white-40": BRIGHT_PARCHMENT + "29",
        "transparent-white-50": BRIGHT_PARCHMENT + "3B",
        "transparent-black-10": VOID + "08", "transparent-black-20": VOID + "12", "transparent-black-30": VOID + "20",
        "transparent-black-40": VOID + "30", "transparent-black-50": VOID + "45",
        "transparent": IRON + "00",
        "text-default": PARCHMENT, "text-muted": OLD_PAPER, "text-secondary": ASH, "text-disabled": FADED_INK,
        "text-over-accent": BRIGHT_PARCHMENT, "text-over-accent-inverted": VOID,
        "text-link": CANDLE_GOLD, "text-error": ERROR_TEXT, "text-warning": CANDLE_GOLD, "text-success": TYPE,
        "editor-text": PARCHMENT,
        "layer-0-bg": OBSIDIAN, "layer-0-border": SOFT_BORDER, "layer-0-bg-inline": INLINE_BG, "layer-0-border-inline": BORDER,
        "layer-1-bg": IRON, "layer-1-border": BORDER, "layer-1-bg-inline": RAISED_IRON, "layer-1-border-inline": "#4A3828",
        "layer-2-bg": RAISED_IRON, "layer-2-bg-inline": SELECTED_IRON, "layer-2-border": BORDER, "layer-2-border-inline": "#4A3828",
        "accent-brand-bg": BRONZE, "accent-brand-border": BRONZE,
        "accent-brand-bg-secondary": BRAND_SECONDARY_BG, "accent-brand-border-secondary": BRAND_SECONDARY_BORDER,
        "accent-error-bg": EMBER_RED, "accent-error-border": EMBER_RED,
        "accent-error-bg-secondary": ERROR_SECONDARY_BG, "accent-error-border-secondary": ERROR_SECONDARY_BORDER,
        "accent-warning-bg": OLD_GOLD, "accent-warning-border": OLD_GOLD,
        "accent-warning-bg-secondary": WARNING_SECONDARY_BG, "accent-warning-border-secondary": WARNING_SECONDARY_BORDER,
        "accent-success-bg": OXIDIZED_BRASS, "accent-success-border": OXIDIZED_BRASS,
        "accent-success-bg-secondary": SUCCESS_SECONDARY_BG, "accent-success-border-secondary": SUCCESS_SECONDARY_BORDER,
        "accent-neutral-bg": ASH, "accent-ai-bg": AI_BG, "accent-ai-border": AI_BORDER,
        "core-bg-transparent-hovered": "transparent-white-20", "core-bg-transparent-pressed": "transparent-white-40",
        "core-border-transparent": "transparent-white-30",
        "dialog-bg": IRON, "dialog-bg-inline": INLINE_BG, "dialog-border": SOFT_BORDER,
        "popup-bg": IRON, "popup-bg-inline": "#1E1814", "popup-border": BORDER, "popup-border-inline": BORDER,
        "editor-bg": OBSIDIAN, "editor-bg-inline": IRON, "editor-border": SOFT_BORDER, "editor-border-inline": BORDER,
        "editor-border-alt": SELECTED_IRON,
        "tool-window-bg": IRON, "tool-window-bg-inline": "#1E1814", "tool-window-bg-alt": INLINE_BG,
        "tool-window-border": SOFT_BORDER, "tool-window-border-inline": BORDER,
        "main-window-bg": VOID, "main-window-bg-alt": "#0F0C0A", "main-window-border": BORDER,
        "control-bg": "dialog-bg", "control-bg-disabled": INJECTED_BG, "control-bg-raised": RAISED_IRON,
        "control-border": BORDER, "control-border-disabled": SOFT_BORDER, "control-border-raised": "#5E5246",
        "control-border-over-accent": "transparent-white-50",
        "control-bg-small": BORDER, "control-bg-small-disabled": SELECTED_IRON, "control-border-small": "#5E5246",
        "control-brand-bg": "accent-brand-bg", "control-brand-border": "accent-brand-border",
        "control-error-bg": "accent-error-bg", "control-error-border": "accent-error-border", "control-error-border-secondary": "#4F2A25",
        "control-warning-bg": "accent-warning-bg", "control-warning-border": "accent-warning-border", "control-warning-border-secondary": "#4A3820",
        "control-success-bg": "accent-success-bg", "control-success-border": "accent-success-border",
        "toolbar-bg-hovered": "core-bg-transparent-hovered", "toolbar-bg-pressed": "core-bg-transparent-pressed",
        "toolbar-border": "core-border-transparent",
        "toolbar-selected-bg": "#5A3E25", "toolbar-selected-bg-hovered": "#644728", "toolbar-selected-bg-active": "accent-brand-bg",
        "toolbar-run-bg": "accent-success-bg", "toolbar-run-bg-hovered": SUCCESS_HOVER,
        "toolbar-stop-bg": WAX_RED, "toolbar-stop-bg-hovered": "#8A4438",
        "feedback-bg": "layer-2-bg", "feedback-border": "layer-2-bg", "feedback-bg-inline": "layer-0-bg",
        "feedback-brand-bg": "accent-brand-bg-secondary", "feedback-brand-border": "accent-brand-border-secondary",
        "feedback-success-bg": "accent-success-bg-secondary", "feedback-success-border": "accent-success-border-secondary",
        "feedback-warning-bg": "accent-warning-bg-secondary", "feedback-warning-border": "accent-warning-border-secondary",
        "feedback-error-bg": "accent-error-bg-secondary", "feedback-error-border": "accent-error-border-secondary",
        "feedback-control-border": "control-border-over-accent", "feedback-ai-bg": "accent-ai-bg", "feedback-ai-border": "accent-ai-border",
        "selection-bg-active": SELECTION, "selection-bg-active-muted": BRAND_SECONDARY_BG,
        "selection-bg-inactive": SELECTED_IRON, "selection-bg-hovered": "transparent-white-10",
        "tab-selected-bg-active": RAISED_IRON, "tab-selected-bg-inactive": TAB_INACTIVE_BG,
        "tab-selected-border-active": BRONZE, "tab-selected-border-inactive": BORDER,
        "tab-bg-hovered": "core-bg-transparent-hovered", "tab-file-color-mask-bg": OBSIDIAN + "80",
        "got-it-bg": "#5A3E25", "got-it-border": "#5A3E25", "got-it-text-link": CANDLE_GOLD, "got-it-text-step": "#877866",
        "got-it-shortcut-bg": "accent-brand-bg-secondary", "got-it-code-border": BRIGHT_PARCHMENT + "70",
        "got-it-contrast-button-bg": "accent-brand-bg-secondary",
        "inlay-bg": "transparent-white-30", "inlay-border": "transparent-white-50",
        "toggle-off-bg": OBSIDIAN, "toggle-button-bg": "#5E5246", "toggle-border": "#5E5246",
        "editor-floating-toolbar-bg": "layer-2-bg", "popup-completion-match-text": CANDLE_GOLD,
        "presentation-assistant-bg": "#5A3E25", "search-match-bg": SEARCH_BG, "tree-indent-guide-border": GUIDE,
        "icon-default-stroke": ICON_STROKE, "icon-over-accent": BRIGHT_PARCHMENT, "icon-green-stroke": TYPE,
        "grad-hor-left": OBSIDIAN + "33", "grad-hor-right": OBSIDIAN + "4D", "grad-ver-top": OBSIDIAN + "1A", "grad-ver-bottom": OBSIDIAN + "80",
    })
    for name, (a1, a1s, a2, bg, *_rest) in PROJECT_GRADIENTS.items():
        c[f"grad-{name}-a1"] = a1 + "FF"
        c[f"grad-{name}-a1-transparent"] = a1 + "00"
        c[f"grad-{name}-a1-secondary"] = a1s
        c[f"grad-{name}-a2"] = a2
        c[f"grad-{name}-bg"] = bg
    return c


# ---- source-colour maps: Rider/Islands colour -> Rise material -----------------
# Keys are upper-case RRGGBB without '#'. Alpha of the source is preserved by the generator.
SCHEME_SOURCE_MAP = {
    "BDBDBD": PARCHMENT, "D0D0D0": PARCHMENT, "F0F0F0": BRIGHT_PARCHMENT,
    "6C95EB": KEYWORD, "C191FF": TYPE, "E1BFFF": TYPE, "39CC9B": CANDLE_GOLD, "66C3CC": PARCHMENT,
    "C9A26D": OLD_GOLD, "ED94C0": COLD_STEEL, "85C46C": ASH, "487D34": OLD_PAPER, "787878": ASH,
    "FF5647": EMBER_RED, "FF8870": EMBER_BRIGHT, "FF919C": "#C4664F", "E67281": EMBER_BRIGHT,
    "F5D86A": CANDLE_GOLD, "D9B72B": OLD_GOLD, "FFD49E": SEARCH_FG, "D688D4": COPPER, "FFBFFE": FADED_GOLD_BRIGHT,
    "FF9259": COPPER, "7DF0C0": CYAN_BRIGHT, "ADEB96": BRASS_BRIGHT, "ADD3FF": COLD_STEEL_BRIGHT, "406AC2": LINK_UNDERLINE,
    "191A1C": OBSIDIAN, "202424": CARET_ROW, "404040": SOFT_BORDER, "303030": TAB_INACTIVE_BG, "343434": RAISED_IRON,
    "383838": IRON, "424242": SOFT_BORDER, "666666": FADED_INK, "686868": FADED_INK, "808080": FADED_INK,
    "909090": ASH, "000000": IRON,
    "232E46": SELECTED_IRON, "293A5F": BORDER, "08335E": SELECTION, "144238": SEARCH_BG, "187057": BRONZE,
    "422240": BORDER, "4A2421": BREAKPOINT_LINE, "612722": "#4F2A25", "502727": ERROR_SECONDARY_BG,
    "B02A2A": WAX_RED, "BF3428": WAX_RED,
    "29421F": DIFF_INSERTED, "2C4722": GUTTER_ADDED, "21331A": "#22231A", "28431B": DIFF_INSERTED, "2D8700": OXIDIZED_BRASS,
    "2B3427": "#1E1B15", "3F2C2B": "#2A1F1B",
    "3A3070": DIFF_MODIFIED, "4D2F6B": BORDER, "522750": USAGE_WRITE_BG, "3B224F": SELECTED_IRON, "03323D": "#22201A",
    "784FB3": FADED_GOLD, "5B4BD6": FADED_GOLD, "36315B": "#2E2620", "A32EA2": FADED_GOLD_BRIGHT, "4C284B": "#2E2620",
    "913C8F": BRONZE,
    "A65426": "#3A2A1F", "7A5C43": COPPER, "6B4C1B": EXEC_POINT, "37300E": WARNING_SECONDARY_BG, "3D3020": RAISED_IRON,
    "493927": "#4A3820", "484012": WARNING_SECONDARY_BG, "8A7F23": OLD_GOLD, "A17100": OLD_GOLD, "4B3D1B": WARNING_SECONDARY_BG,
    "09434D": "#22201A", "1B4043": "#212525", "007C87": COLD_STEEL, "1F858F": COLD_STEEL, "13362E": "#22231A",
    "332C29": INJECTED_BG, "FF00FF": FADED_GOLD,
}

UI_SOURCE_MAP = {
    "FFFFFF": BRIGHT_PARCHMENT, "000000": VOID,
    "2F5EB9": BRONZE, "2A6E47": SUCCESS_HOVER, "6C4EBB": "#6B583C",
    "F0AC81": COLD_STEEL_BRIGHT, "6F737A": ASH, "548AF7": CANDLE_GOLD, "9FA2A8": OLD_PAPER,
    "371B1C": "#2A1816", "DB5C5C": EMBER_BRIGHT, "56272B": ERROR_SECONDARY_BG, "73767C": ASH,
    "291F1C": "#2A2318", "1C261C": "#22231A", "45322B": "#2E2118", "472B2B": "#2E1D1B", "3B3147": "#2A2420",
    "1D3D3B": "#1F2423", "35363B": "#211E1B",
    "3573F0": OLD_GOLD, "3574F0": OLD_GOLD, "2B2D30": RAISED_IRON, "393B40": SELECTED_IRON, "868A91": OLD_PAPER,
    "35538F": BRONZE, "43454A": BORDER, "5A5D63": "#5E5246", "262626": OBSIDIAN, "808080": BRONZE,
    "9DA0A8": "#B09A7A", "3671E5": BRONZE, "366ACF": BRONZE, "CED0D6": PARCHMENT, "B4B8BF": "#B8A180",
    "5FAD65": TYPE, "273828": SUCCESS_SECONDARY_BG, "4E8052": SUCCESS_HOVER, "375239": "#383621",
    "D6AE58": CANDLE_GOLD, "3D3223": WARNING_SECONDARY_BG, "826A41": "#7A5A33", "5E4D33": WARNING_SECONDARY_BORDER,
    "E37774": "#C4664F", "402929": ERROR_SECONDARY_BG, "BD5757": EMBER_RED, "1D2336": "#2A2118",
    "F5D273": CANDLE_GOLD, "B589EC": FADED_GOLD_BRIGHT, "57965C": OXIDIZED_BRASS, "4E5157": "#4A3828",
    "F2C55C": CANDLE_GOLD, "131314": VOID, "575A5C": "#5E5246", "55339C": "#5B4A32", "212326": IRON,
    "1E1F22": OBSIDIAN, "F0F1F2": BRIGHT_PARCHMENT, "888888": ASH, "26282C": INLINE_BG, "33353B": SELECTED_IRON,
    "DFE1E5": BRIGHT_PARCHMENT, "27282A": "#1E1814",
}

# new-UI SVG icon colours -> Rise (see ref/icon-colors.json); remaining colours fall back to materialize()
ICON_SOURCE_MAP = {
    "CED0D6": ICON_STROKE, "43454A": SELECTED_IRON, "548AF7": OLD_GOLD, "3574F0": OLD_GOLD, "DB5C5C": EMBER_RED,
    "57965C": OXIDIZED_BRASS, "5FAD65": TYPE, "25324D": "#2A2118", "253627": "#22231A", "402929": ERROR_SECONDARY_BG,
    "3D3223": "#3A2C18", "45322B": "#3A2A1F", "322936": "#2E2620", "2F2936": "#2E2620", "C77D55": COPPER,
    "E08855": "#C4875A", "F26522": COPPER, "F2C55C": CANDLE_GOLD, "D6AE58": CANDLE_GOLD, "F4AF3D": CANDLE_GOLD,
    "F5D273": "#C9A268", "BA9752": OLD_GOLD, "B589EC": FADED_GOLD_BRIGHT, "A571E6": FADED_GOLD_BRIGHT,
    "BB69D6": FADED_GOLD_BRIGHT, "955AE0": FADED_GOLD, "8150BE": FADED_GOLD, "6800EE": "#6B583C", "465FF3": LINK_UNDERLINE,
    "20C9FF": COLD_STEEL_BRIGHT, "868A91": OLD_PAPER, "6F737A": ASH, "9DA0A8": "#B09A7A", "9AA7B0": "#B09A7A",
    "B4B8BF": "#B8A180", "5A5D63": "#5E5246", "6C707E": ASH, "1E1F22": OBSIDIAN, "2B2D30": RAISED_IRON,
    "F0F1F2": BRIGHT_PARCHMENT, "DFE1E6": BRIGHT_PARCHMENT, "24A394": COLD_STEEL, "40B6E0": COLD_STEEL_BRIGHT,
    "2E436E": BRAND_SECONDARY_BG, "5E3838": "#4F2A25", "231F20": IRON, "503E68": AI_BORDER, "7777E9": LINK_UNDERLINE,
    "01009A": "#5A3E25", "01B202": OXIDIZED_BRASS, "0FE90F": TYPE, "B83535": EMBER_RED, "FD5B5A": EMBER_BRIGHT,
    "2C2255": "#2A2015", "D33833": EMBER_RED, "DCD9D8": BRIGHT_PARCHMENT, "F7E4CD": "#E3D4BC", "375239": "#383621",
}

# classic named icon palette (older-style icons in third-party plugins)
ICON_NAMED_PALETTE = {
    "Actions.Blue": OLD_GOLD, "Actions.Green": OXIDIZED_BRASS, "Actions.Red": EMBER_RED, "Actions.Yellow": CANDLE_GOLD,
    "Actions.Grey": OLD_PAPER, "Actions.GreyInline": OLD_PAPER, "Actions.GreyInline.Dark": PARCHMENT,
    "Objects.Blue": OLD_GOLD, "Objects.Green": OXIDIZED_BRASS, "Objects.GreenAndroid": OXIDIZED_BRASS,
    "Objects.Red": EMBER_RED, "Objects.RedStatus": EMBER_RED, "Objects.Yellow": CANDLE_GOLD, "Objects.YellowDark": OLD_GOLD,
    "Objects.Purple": FADED_GOLD, "Objects.Pink": FADED_GOLD_BRIGHT, "Objects.Grey": OLD_PAPER, "Objects.BlackText": OBSIDIAN,
    # new-UI checkbox palette keys (the ".Dark" variants are deprecated and Focus.Thin.* unsupported - idea.log)
    "Checkbox.Background.Default": IRON, "Checkbox.Border.Default": "#5E5246",
    "Checkbox.Background.Selected": BRONZE, "Checkbox.Border.Selected": BRONZE,
    "Checkbox.Foreground.Selected": BRIGHT_PARCHMENT,
    "Checkbox.Focus.Wide": BRONZE,
    "Checkbox.Background.Disabled": OBSIDIAN, "Checkbox.Border.Disabled": FADED_INK,
    "Checkbox.Foreground.Disabled": ASH,
}


# ---- colour math ---------------------------------------------------------------
def parse(hexstr):
    """'#RRGGBB', '#RRGGBBAA', 'RRGGBB', 'RRGGBBAA' or IntelliJ short ints like 'FF00' -> (r,g,b,a|None)."""
    s = hexstr.strip().lstrip("#")
    if len(s) in (7, 8):
        v = int(s, 16)
        return ((v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, v & 255)
    v = int(s, 16)
    return ((v >> 16) & 255, (v >> 8) & 255, v & 255, None)


def to_hex(r, g, b, a=None, prefix="#"):
    s = f"{prefix}{r:02X}{g:02X}{b:02X}"
    return s + (f"{a:02X}" if a is not None else "")


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexstr):
    r, g, b, _ = parse(hexstr)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def lstar(hexstr):
    y = luminance(hexstr)
    f = y ** (1 / 3) if y > 0.008856 else 7.787 * y + 16 / 116
    return 116 * f - 16


def materialize(hexstr):
    """Map an arbitrary colour into the Rise ramps by hue family + perceived lightness. Keeps alpha."""
    r, g, b, a = parse(hexstr)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    hd = h * 360
    if s < 0.14 or v < 0.06:
        fam = "gray"
    elif hd < 18 or hd >= 335:
        fam = "red"
    elif hd < 42:
        fam = "orange"
    elif hd < 72:
        fam = "yellow"
    elif hd < 165:
        fam = "green"
    elif hd < 265:
        fam = "teal"
    else:
        fam = "purple"
    target = lstar(to_hex(r, g, b))
    best = min(RAMPS[fam], key=lambda c: abs(lstar(c) - target))
    rr, gg, bb, _ = parse(best)
    return to_hex(rr, gg, bb, a)


def remap(hexstr, table):
    """Look the RGB part up in `table` (upper-case RRGGBB keys), else materialize. Alpha preserved."""
    r, g, b, a = parse(hexstr)
    key = f"{r:02X}{g:02X}{b:02X}"
    if key in table:
        rr, gg, bb, _ = parse(table[key])
        return to_hex(rr, gg, bb, a)
    return materialize(hexstr)
