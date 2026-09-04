# Rise / Codex — odchylky od zadání (v1.0.0)

Odsouhlaseno 2026-09-04. Vztahuje se k `rise_codex_ide_theme_spec.md`.

1. **Keywords vs. control flow** — Rider nemá pro C# samostatný klíč pro control‑flow klíčová slova
   (vše je `DEFAULT_KEYWORD`), spec navíc uvádí `return` v obou kategoriích. Všechna klíčová slova mají
   jednu barvu. Copper zůstává pro atributy, escape sekvence a eventy.
2. **Kontrast** (proti editoru `#110E0C`): rust `#9A5635` = 3.4:1 a oxidized brass `#77704E` = 3.9:1 by
   byly slabší než obyčejný text (parchment 9:1). Klíčová slova → **`#B9663D`** (4.6:1), typy →
   **`#8E8663`** (5.3:1). `#77704E` zůstává pro success/valid, run tlačítko a ANSI green.
3. **Chybový text** v tool windows a konzoli **`#B75A49`** (4.0:1 na iron); vlnovky a error stripe
   zůstávají `#A14D3E`.
4. **Primární UI text** je parchment `#C7AE87` (spec: old‑paper `#9E8768`); old‑paper slouží pro
   sekundární/info text, popisky a parametry.
5. **Selection foreground** není nastaven — uvnitř výběru zůstává zvýraznění syntaxe.
6. **Warnings** sdílejí candle‑gold `#C09152` s názvy metod (dle spec). Volitelná úprava do budoucna:
   vlastní tón `#D29C4B`.
7. **Terminál cyan** `#7F8580` → `#7E9489`, aby šel v PowerShellu/`ls` rozlišit od blue `#748080`.
8. **Doplněné hodnoty**, které spec neuvádí: caret row `#171210`, matched brace, usages `#2A211A`/`#33261B`,
   execution point `#4A3418`, breakpoint line `#3A211D`, diff `#2A2B1C`/`#2E2418`/`#2E1B18`, gutter VCS
   `#4A4A2E`/`#6E5033`/`#783A32`, inlay hints, folded text, odkazy (candle‑gold s podtržením `#8A6338`),
   TODO, scrollbar (bronze s alfou), hover/disabled, paleta ikon, barvy projektů, AI accent (faded gold).
9. **Islands** — spec chce rám okna nejtmavší (void) a editor/tool windows světlejší; Islands má
   výchozí opak. Držíme spec: ostrovy ze železa na sazích, rozložení Islands zůstává.
10. **Phase 3, co JetBrains theme neumí**: splash screen, ornamenty/separátory, latinské popisky,
    číslování workspace, Omarchy. Realizováno: přebarvení ikon (mapa `icons.ColorPalette`, ~160 barev),
    terminálová paleta, motto v popisu pluginu a jako pozdrav v terminálu IDE (PowerShell profil,
    jen když `TERMINAL_EMULATOR = JetBrains-JediTerm`), UI font Cambria jako globální nastavení Rideru.
11. **Fonty**: editor Iosevka Term 17 / 1.2 / ligatury je zapsán přímo ve schématu (stejný mechanismus,
    jakým to dnes drží kopie Gruvboxu). UI font Cambria 13 v `options\other.xml`.
12. **XML/HTML tagy** používají barvu typů (brass) místo rust — v XML jsou tagy ~40 % tokenů a rust by
    porušil zásadu „60–70 % textu v parchment/neutral“.

## v1.0.1 (po první kontrole v IDE, 2026-09-04)

13. **Text lift**: textové tokeny jsou o půl kroku světlejší a sytější (`palette.TEXT_LIFT = 0.5`:
    +5 % světlost, ×1.125 sytost v HLS). Např. parchment `#C7AE87` → `#D3BA95`, keyword `#B9663D` → `#CB7144`,
    typy `#8E8663` → `#9E956D`, strings `#A37843` → `#BC8644`, komentáře `#75685A` → `#857563`.
    Pozadí, rámečky a akcentní výplně (bronze, wax, ember) zůstávají dle spec. `TEXT_LIFT = 0` vrací spec,
    `1` je plný krok.
14. **Islands `Island.inactiveAlpha`** 0.56 → 0.85: Rider kreslí neaktivní ostrovy průhledně přes rám (void),
    což tlumilo veškerý text mimo fokus výrazně víc než v HTML náhledu.
15. **Checkbox** klíče v paletě ikon bez přípony `.Dark` (nové UI je má zastaralé), `Focus.Thin.*` odstraněny.
