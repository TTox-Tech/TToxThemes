"""VS Code colour theme extension: one folder, three themes.

dist/apps/vscode/ttox-themes/{package.json,README.md,themes/ttox-<variant>-color-theme.json}

VS Code windows are opaque, so the opacity ladder does not apply; surfaces use the ladder's base colours
(editor/terminal = bg, popups = raised, inputs = surface). Accent is used only where SPEC section 3 allows it.
"""
from __future__ import annotations
import json
import lib

NAME = "apps_vscode"; PACK = "apps"; ONCE = True
EXT_NAME = "ttox-themes"; EXT_PUBLISHER = "ttox"; EXT_VERSION = "0.1.0"
SIDEBAR_DARKEN = 0.12   # "sidebars slightly darker than body"; no token for this


def roles(p: dict) -> dict:
    """Syntax roles drawn from the palette's 16 terminal colours (already on-palette, muted)."""
    t = p["term"]
    return {
        "comment": p["muted"], "text": p["fg"], "strong": p["fg_hi"], "keyword": p["accent_text"],
        "string": t[10], "number": t[11], "type": t[14], "escape": t[6],
        # a soft neutral that never collides with the keyword colour
        "prop": t[12] if t[12].lower() != p["accent_text"].lower() else t[13],
        "invalid": p["err"], "ok": p["ok"], "warn": p["warn"], "err": p["err"],
    }


def workbench(p: dict, tk: dict) -> dict:
    a = lib.hex_alpha
    bg, surface, raised, line, muted = p["bg"], p["surface"], p["raised"], p["line"], p["muted"]
    fg, fg_hi, accent, accent2, atext = p["fg"], p["fg_hi"], p["accent"], p["accent2"], p["accent_text"]
    side = lib.darken(bg, SIDEBAR_DARKEN)
    sel = a(accent, tk["wash"]["select_alpha"]); hover = a(fg, tk["wash"]["hover_alpha"])
    hair = a(fg, tk["border"]["hairline_alpha"]); sep = a(line, tk["border"]["sep_alpha"])
    side_sep = a(line, 0.40)
    none = a(bg, 0.0)
    c = {
        # base
        "focusBorder": accent, "foreground": fg, "disabledForeground": muted, "descriptionForeground": muted,
        "errorForeground": p["err"], "icon.foreground": fg, "selection.background": sel,
        "widget.shadow": a("#000000", 0.30), "widget.border": hair, "sash.hoverBorder": accent,
        "textLink.foreground": atext, "textLink.activeForeground": fg_hi, "textPreformat.foreground": fg_hi,
        "textBlockQuote.background": surface, "textBlockQuote.border": line, "textCodeBlock.background": surface,
        "textSeparator.foreground": line,
        # window / title bar: one sheet with the body
        "window.activeBorder": a(fg, tk["border"]["active_alpha"]), "window.inactiveBorder": line,
        "titleBar.activeBackground": bg, "titleBar.activeForeground": fg, "titleBar.inactiveBackground": bg,
        "titleBar.inactiveForeground": muted, "titleBar.border": sep,
        "menubar.selectionBackground": hover, "menubar.selectionForeground": fg_hi,
        "menu.background": raised, "menu.foreground": fg, "menu.selectionBackground": sel,
        "menu.selectionForeground": fg_hi, "menu.separatorBackground": line, "menu.border": hair,
        "commandCenter.background": surface, "commandCenter.foreground": muted, "commandCenter.border": line,
        "commandCenter.activeBackground": hover, "commandCenter.activeForeground": fg_hi,
        # activity bar
        "activityBar.background": side, "activityBar.foreground": fg_hi, "activityBar.inactiveForeground": muted,
        "activityBar.border": side_sep, "activityBar.activeBorder": accent, "activityBar.activeBackground": none,
        "activityBarBadge.background": line, "activityBarBadge.foreground": fg_hi,
        "activityBarTop.foreground": fg_hi, "activityBarTop.inactiveForeground": muted,
        "activityBarTop.activeBorder": accent,
        # side bar
        "sideBar.background": side, "sideBar.foreground": fg, "sideBar.border": side_sep,
        "sideBarTitle.foreground": muted, "sideBarSectionHeader.background": side,
        "sideBarSectionHeader.foreground": fg, "sideBarSectionHeader.border": sep,
        # lists / trees
        "list.activeSelectionBackground": sel, "list.activeSelectionForeground": fg_hi,
        "list.inactiveSelectionBackground": a(accent2, tk["wash"]["select_alpha"]),
        "list.inactiveSelectionForeground": fg, "list.hoverBackground": hover, "list.hoverForeground": fg_hi,
        "list.focusBackground": sel, "list.focusForeground": fg_hi, "list.focusOutline": accent,
        "list.highlightForeground": atext, "list.focusHighlightForeground": atext,
        "list.dropBackground": sel, "list.errorForeground": p["err"], "list.warningForeground": p["warn"],
        "list.deemphasizedForeground": muted, "list.filterMatchBackground": a(accent, 0.20),
        "tree.indentGuidesStroke": line, "tree.inactiveIndentGuidesStroke": sep,
        # editor groups / tabs: underline style
        "editorGroup.border": sep, "editorGroup.dropBackground": a(accent, 0.12),
        "editorGroupHeader.tabsBackground": bg, "editorGroupHeader.tabsBorder": sep,
        "editorGroupHeader.noTabsBackground": bg, "editorGroupHeader.border": sep,
        "tab.activeBackground": bg, "tab.activeForeground": fg_hi, "tab.activeBorder": accent,
        "tab.activeBorderTop": none, "tab.inactiveBackground": bg, "tab.inactiveForeground": muted,
        "tab.unfocusedActiveBackground": bg, "tab.unfocusedActiveForeground": fg,
        "tab.unfocusedActiveBorder": accent2, "tab.unfocusedInactiveForeground": muted,
        "tab.border": none, "tab.hoverBackground": hover, "tab.hoverForeground": fg_hi,
        "tab.lastPinnedBorder": line, "tab.activeModifiedBorder": none, "tab.inactiveModifiedBorder": none,
        "breadcrumb.background": bg, "breadcrumb.foreground": muted, "breadcrumb.focusForeground": fg_hi,
        "breadcrumb.activeSelectionForeground": fg_hi, "breadcrumbPicker.background": raised,
        # editor
        "editor.background": bg, "editor.foreground": fg, "editorCursor.foreground": fg,
        "editorCursor.background": bg, "editorLineNumber.foreground": lib.mix(line, muted, 0.5),
        "editorLineNumber.activeForeground": fg, "editor.lineHighlightBackground": a(fg, 0.04),
        "editor.lineHighlightBorder": none, "editor.selectionBackground": sel,
        "editor.inactiveSelectionBackground": a(accent2, tk["wash"]["select_alpha"]),
        "editor.selectionHighlightBackground": a(accent, 0.14), "editor.wordHighlightBackground": a(fg, 0.10),
        "editor.wordHighlightStrongBackground": a(accent, 0.18),
        "editor.findMatchBackground": a(p["warn"], 0.40), "editor.findMatchHighlightBackground": a(p["warn"], 0.18),
        "editor.findRangeHighlightBackground": a(fg, 0.05), "editor.hoverHighlightBackground": a(fg, 0.08),
        "editor.rangeHighlightBackground": a(fg, 0.05), "editor.foldBackground": a(fg, 0.04),
        "editorLink.activeForeground": atext, "editorWhitespace.foreground": a(muted, 0.35),
        "editorIndentGuide.background1": a(line, 0.60), "editorIndentGuide.activeBackground1": muted,
        "editorIndentGuide.background": a(line, 0.60), "editorIndentGuide.activeBackground": muted,
        "editorRuler.foreground": sep, "editorCodeLens.foreground": muted,
        "editorBracketMatch.background": a(fg, 0.10), "editorBracketMatch.border": muted,
        "editorBracketHighlight.foreground1": fg, "editorBracketHighlight.foreground2": atext,
        "editorBracketHighlight.foreground3": p["term"][14], "editorBracketHighlight.foreground4": fg,
        "editorBracketHighlight.foreground5": atext, "editorBracketHighlight.foreground6": p["term"][14],
        "editorBracketHighlight.unexpectedBracket.foreground": p["err"],
        "editorError.foreground": p["err"], "editorWarning.foreground": p["warn"], "editorInfo.foreground": atext,
        "editorHint.foreground": muted, "editorUnnecessaryCode.opacity": a("#000000", 0.67),
        "editorGhostText.foreground": a(muted, 0.80), "editorInlayHint.foreground": muted,
        "editorInlayHint.background": a(fg, 0.06),
        "editorGutter.background": bg, "editorGutter.addedBackground": p["ok"],
        "editorGutter.modifiedBackground": p["warn"], "editorGutter.deletedBackground": p["err"],
        "editorGutter.foldingControlForeground": muted,
        "editorOverviewRuler.border": none, "editorOverviewRuler.errorForeground": p["err"],
        "editorOverviewRuler.warningForeground": p["warn"], "editorOverviewRuler.infoForeground": atext,
        "editorOverviewRuler.findMatchForeground": a(p["warn"], 0.70),
        "editorOverviewRuler.selectionHighlightForeground": a(accent, 0.60),
        "editorOverviewRuler.addedForeground": a(p["ok"], 0.70),
        "editorOverviewRuler.modifiedForeground": a(p["warn"], 0.70),
        "editorOverviewRuler.deletedForeground": a(p["err"], 0.70),
        "editorStickyScroll.background": bg, "editorStickyScrollHover.background": surface,
        # editor widgets / popups: raised + hairline
        "editorWidget.background": raised, "editorWidget.foreground": fg, "editorWidget.border": hair,
        "editorWidget.resizeBorder": accent, "editorSuggestWidget.background": raised,
        "editorSuggestWidget.border": hair, "editorSuggestWidget.foreground": fg,
        "editorSuggestWidget.selectedBackground": sel, "editorSuggestWidget.selectedForeground": fg_hi,
        "editorSuggestWidget.highlightForeground": atext, "editorSuggestWidget.focusHighlightForeground": atext,
        "editorHoverWidget.background": raised, "editorHoverWidget.border": hair,
        "editorHoverWidget.foreground": fg, "editorHoverWidget.statusBarBackground": surface,
        "peekView.border": line, "peekViewEditor.background": surface, "peekViewEditorGutter.background": surface,
        "peekViewEditor.matchHighlightBackground": a(p["warn"], 0.30), "peekViewResult.background": raised,
        "peekViewResult.fileForeground": fg, "peekViewResult.lineForeground": muted,
        "peekViewResult.matchHighlightBackground": a(p["warn"], 0.30),
        "peekViewResult.selectionBackground": sel, "peekViewResult.selectionForeground": fg_hi,
        "peekViewTitle.background": raised, "peekViewTitleLabel.foreground": fg_hi,
        "peekViewTitleDescription.foreground": muted,
        # diff / merge
        "diffEditor.insertedTextBackground": a(p["ok"], 0.16), "diffEditor.removedTextBackground": a(p["err"], 0.16),
        "diffEditor.insertedLineBackground": a(p["ok"], 0.10), "diffEditor.removedLineBackground": a(p["err"], 0.10),
        "diffEditor.diagonalFill": sep, "diffEditor.border": sep,
        "merge.currentHeaderBackground": a(p["ok"], 0.35), "merge.currentContentBackground": a(p["ok"], 0.14),
        "merge.incomingHeaderBackground": a(atext, 0.35), "merge.incomingContentBackground": a(atext, 0.14),
        "merge.commonHeaderBackground": a(muted, 0.35), "merge.commonContentBackground": a(muted, 0.14),
        # controls
        "button.background": accent, "button.foreground": fg_hi, "button.hoverBackground": lib.mix(accent, accent2, 0.5),
        "button.border": none, "button.secondaryBackground": raised, "button.secondaryForeground": fg,
        "button.secondaryHoverBackground": lib.mix(raised, line, 0.5), "button.separator": a(fg_hi, 0.30),
        "checkbox.background": surface, "checkbox.border": line, "checkbox.foreground": fg_hi,
        "dropdown.background": surface, "dropdown.listBackground": raised, "dropdown.border": line,
        "dropdown.foreground": fg,
        "input.background": surface, "input.foreground": fg, "input.border": line,
        "input.placeholderForeground": muted, "inputOption.activeBackground": sel,
        "inputOption.activeBorder": accent, "inputOption.activeForeground": fg_hi,
        "inputOption.hoverBackground": hover,
        "inputValidation.errorBackground": lib.over(p["err"], raised, 0.25), "inputValidation.errorBorder": p["err"],
        "inputValidation.warningBackground": lib.over(p["warn"], raised, 0.25),
        "inputValidation.warningBorder": p["warn"],
        "inputValidation.infoBackground": raised, "inputValidation.infoBorder": line,
        "scrollbar.shadow": none, "scrollbarSlider.background": a(muted, 0.50),
        "scrollbarSlider.hoverBackground": a(muted, 0.70), "scrollbarSlider.activeBackground": a(fg, 0.60),
        "badge.background": line, "badge.foreground": fg_hi, "progressBar.background": accent,
        "toolbar.hoverBackground": hover, "toolbar.activeBackground": a(fg, 0.10),
        "keybindingLabel.background": surface, "keybindingLabel.foreground": fg,
        "keybindingLabel.border": line, "keybindingLabel.bottomBorder": line,
        # quick input (launcher-like)
        "quickInput.background": raised, "quickInput.foreground": fg, "quickInputTitle.background": raised,
        "quickInputList.focusBackground": sel, "quickInputList.focusForeground": fg_hi,
        "pickerGroup.border": line, "pickerGroup.foreground": muted,
        # panel / terminal
        "panel.background": bg, "panel.border": sep, "panelTitle.activeBorder": accent,
        "panelTitle.activeForeground": fg_hi, "panelTitle.inactiveForeground": muted,
        "panelInput.border": line, "panelSection.border": sep, "panelSectionHeader.background": bg,
        "terminal.background": bg, "terminal.foreground": fg, "terminal.selectionBackground": sel,
        "terminalCursor.foreground": fg, "terminalCursor.background": bg, "terminal.border": sep,
        "terminal.tab.activeBorder": accent,
        # status bar
        "statusBar.background": side, "statusBar.foreground": muted, "statusBar.border": side_sep,
        "statusBar.noFolderBackground": side, "statusBar.noFolderForeground": muted,
        "statusBar.debuggingBackground": lib.over(p["warn"], side, 0.30), "statusBar.debuggingForeground": fg_hi,
        "statusBar.focusBorder": accent, "statusBarItem.hoverBackground": hover,
        "statusBarItem.hoverForeground": fg_hi, "statusBarItem.activeBackground": a(fg, 0.10),
        "statusBarItem.remoteBackground": side, "statusBarItem.remoteForeground": atext,
        "statusBarItem.prominentBackground": surface, "statusBarItem.prominentForeground": fg,
        "statusBarItem.errorBackground": lib.over(p["err"], side, 0.40), "statusBarItem.errorForeground": fg_hi,
        "statusBarItem.warningBackground": lib.over(p["warn"], side, 0.40),
        "statusBarItem.warningForeground": fg_hi,
        # notifications
        "notificationCenter.border": hair, "notificationCenterHeader.background": raised,
        "notificationCenterHeader.foreground": fg, "notificationToast.border": hair,
        "notifications.background": raised, "notifications.foreground": fg, "notifications.border": sep,
        "notificationLink.foreground": atext, "notificationsErrorIcon.foreground": p["err"],
        "notificationsWarningIcon.foreground": p["warn"], "notificationsInfoIcon.foreground": atext,
        # misc views
        "extensionButton.prominentBackground": accent, "extensionButton.prominentForeground": fg_hi,
        "extensionButton.prominentHoverBackground": lib.mix(accent, accent2, 0.5),
        "extensionBadge.remoteBackground": line, "extensionBadge.remoteForeground": fg_hi,
        "settings.headerForeground": fg_hi, "settings.modifiedItemIndicator": accent,
        "settings.dropdownBackground": surface, "settings.dropdownBorder": line,
        "settings.checkboxBackground": surface, "settings.checkboxBorder": line,
        "settings.textInputBackground": surface, "settings.textInputBorder": line,
        "settings.numberInputBackground": surface, "settings.numberInputBorder": line,
        "settings.focusedRowBackground": hover, "settings.rowHoverBackground": a(fg, 0.03),
        "welcomePage.tileBackground": surface, "welcomePage.tileHoverBackground": raised,
        "welcomePage.tileBorder": line, "welcomePage.progress.foreground": accent,
        "welcomePage.progress.background": line, "walkThrough.embeddedEditorBackground": surface,
        "minimap.background": bg, "minimap.selectionHighlight": a(accent, 0.60),
        "minimap.findMatchHighlight": a(p["warn"], 0.60), "minimap.errorHighlight": p["err"],
        "minimap.warningHighlight": p["warn"], "minimapSlider.background": a(muted, 0.20),
        "minimapSlider.hoverBackground": a(muted, 0.35), "minimapSlider.activeBackground": a(muted, 0.50),
        "minimapGutter.addedBackground": p["ok"], "minimapGutter.modifiedBackground": p["warn"],
        "minimapGutter.deletedBackground": p["err"],
        "gitDecoration.addedResourceForeground": p["ok"], "gitDecoration.modifiedResourceForeground": p["warn"],
        "gitDecoration.deletedResourceForeground": p["err"], "gitDecoration.renamedResourceForeground": p["ok"],
        "gitDecoration.untrackedResourceForeground": p["term"][10],
        "gitDecoration.ignoredResourceForeground": muted, "gitDecoration.conflictingResourceForeground": p["term"][9],
        "gitDecoration.stageModifiedResourceForeground": p["warn"],
        "gitDecoration.stageDeletedResourceForeground": p["err"],
        "gitDecoration.submoduleResourceForeground": muted,
        "debugToolBar.background": raised, "debugToolBar.border": hair,
        "debugIcon.breakpointForeground": p["err"], "debugIcon.startForeground": p["ok"],
        "debugIcon.stopForeground": p["err"], "debugIcon.pauseForeground": p["warn"],
        "editor.stackFrameHighlightBackground": a(p["warn"], 0.20),
        "editor.focusedStackFrameHighlightBackground": a(p["ok"], 0.20),
        "debugConsole.errorForeground": p["err"], "debugConsole.warningForeground": p["warn"],
        "debugConsole.infoForeground": fg, "debugConsoleInputIcon.foreground": atext,
        "testing.iconPassed": p["ok"], "testing.iconFailed": p["err"], "testing.iconErrored": p["err"],
        "testing.iconQueued": p["warn"], "testing.iconSkipped": muted, "testing.iconUnset": muted,
        "charts.foreground": fg, "charts.lines": line, "charts.red": p["err"], "charts.green": p["ok"],
        "charts.yellow": p["warn"], "charts.blue": p["term"][12], "charts.purple": p["term"][13],
        "charts.orange": p["term"][11],
        "symbolIcon.classForeground": p["term"][14], "symbolIcon.functionForeground": fg_hi,
        "symbolIcon.methodForeground": fg_hi, "symbolIcon.keywordForeground": atext,
        "symbolIcon.variableForeground": fg, "symbolIcon.stringForeground": p["term"][10],
        "symbolIcon.numberForeground": p["term"][11], "symbolIcon.constantForeground": p["term"][11],
        "problemsErrorIcon.foreground": p["err"], "problemsWarningIcon.foreground": p["warn"],
        "problemsInfoIcon.foreground": atext,
        "banner.background": surface, "banner.foreground": fg, "banner.iconForeground": atext,
        "chat.requestBackground": surface, "chat.requestBorder": line,
        "inlineChat.background": raised, "inlineChat.border": hair,
        "notebook.editorBackground": bg, "notebook.cellBorderColor": line,
        "notebook.focusedCellBorder": accent, "notebook.cellEditorBackground": surface,
        "notebook.selectedCellBackground": a(fg, 0.04), "notebook.cellToolbarSeparator": line,
    }
    for i, name in enumerate(["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]):
        c[f"terminal.ansi{name}"] = p["term"][i]
        c[f"terminal.ansiBright{name}"] = p["term"][i + 8]
    return dict(sorted(c.items()))


def token_colors(p: dict) -> list:
    r = roles(p)

    def rule(name: str, scope: list, fg: str | None = None, style: str | None = None) -> dict:
        s: dict = {}
        if fg: s["foreground"] = fg
        if style is not None: s["fontStyle"] = style
        return {"name": name, "scope": scope, "settings": s}

    return [
        rule("Comment", ["comment", "punctuation.definition.comment", "string.comment"], r["comment"], "italic"),
        rule("Text", ["source", "text", "variable", "variable.other", "meta.embedded"], r["text"]),
        rule("Punctuation", ["punctuation", "meta.brace", "punctuation.separator", "punctuation.terminator",
                             "punctuation.section"], lib.mix(p["muted"], p["fg"], 0.5)),
        rule("Operator", ["keyword.operator", "punctuation.accessor"], r["text"]),
        rule("Keyword", ["keyword", "keyword.control", "storage", "storage.type", "storage.modifier",
                         "keyword.operator.new", "keyword.operator.expression", "keyword.operator.logical.python",
                         "keyword.other.unit", "variable.language"], r["keyword"]),
        rule("String", ["string", "string.quoted", "string.template", "punctuation.definition.string",
                        "markup.inline.raw", "markup.fenced_code.block"], r["string"]),
        rule("Escape and regex", ["constant.character.escape", "string.regexp", "constant.other.placeholder",
                                  "punctuation.definition.template-expression", "punctuation.section.embedded"],
             r["escape"]),
        rule("Number and constant", ["constant.numeric", "constant.language", "constant.character",
                                     "constant.other", "support.constant", "variable.other.constant",
                                     "variable.other.enummember"], r["number"]),
        rule("Function", ["entity.name.function", "support.function", "meta.function-call",
                          "variable.function", "entity.name.command", "meta.function-call.generic"], r["strong"]),
        rule("Type and class", ["entity.name.type", "entity.name.class", "entity.name.namespace",
                                "entity.other.inherited-class", "support.type", "support.class",
                                "entity.name.struct", "entity.name.enum", "entity.name.interface",
                                "storage.type.primitive", "storage.type.built-in"], r["type"]),
        rule("Property and attribute", ["variable.other.property", "variable.other.object.property",
                                        "support.variable.property", "meta.object-literal.key",
                                        "entity.other.attribute-name", "support.type.property-name",
                                        "variable.other.member", "entity.name.tag.yaml",
                                        "keyword.other.definition.ini"], r["prop"]),
        rule("Parameter", ["variable.parameter", "meta.parameter"], r["text"], "italic"),
        rule("Tag", ["entity.name.tag", "punctuation.definition.tag", "meta.tag.sgml"], r["keyword"]),
        rule("Decorator", ["meta.decorator", "entity.name.function.decorator", "punctuation.decorator",
                           "meta.annotation", "storage.type.annotation"], r["prop"], "italic"),
        rule("Invalid", ["invalid", "invalid.illegal"], r["invalid"]),
        rule("Deprecated", ["invalid.deprecated"], r["warn"], "strikethrough"),
        rule("Markup heading", ["markup.heading", "entity.name.section", "punctuation.definition.heading"],
             r["strong"], "bold"),
        rule("Markup bold", ["markup.bold"], r["strong"], "bold"),
        rule("Markup italic", ["markup.italic"], None, "italic"),
        rule("Markup strikethrough", ["markup.strikethrough"], None, "strikethrough"),
        rule("Markup link", ["markup.underline.link", "string.other.link", "meta.link"], r["keyword"], "underline"),
        rule("Markup quote", ["markup.quote"], r["comment"], "italic"),
        rule("Markup list marker", ["punctuation.definition.list.begin", "beginning.punctuation.definition.list"],
             r["keyword"]),
        rule("Diff inserted", ["markup.inserted", "meta.diff.header.to-file", "punctuation.definition.inserted"],
             r["ok"]),
        rule("Diff deleted", ["markup.deleted", "meta.diff.header.from-file", "punctuation.definition.deleted"],
             r["err"]),
        rule("Diff changed", ["markup.changed", "meta.diff.range", "meta.diff.header"], r["warn"]),
        rule("JSON key", ["support.type.property-name.json", "meta.structure.dictionary.key.python"], r["prop"]),
        rule("CSS selector", ["entity.other.attribute-name.class.css", "entity.other.attribute-name.id.css",
                              "entity.other.attribute-name.pseudo-class.css",
                              "entity.other.attribute-name.pseudo-element.css"], r["type"]),
        rule("CSS property", ["support.type.property-name.css", "meta.property-name"], r["text"]),
        rule("Shell variable", ["variable.other.normal.shell", "variable.other.bracket.shell",
                                "punctuation.definition.variable.shell", "variable.other.special.shell"], r["prop"]),
    ]


def semantic(p: dict) -> dict:
    r = roles(p)
    return {
        "class": r["type"], "comment": {"foreground": r["comment"], "italic": True}, "decorator": r["prop"],
        "enum": r["type"], "enumMember": r["number"], "function": r["strong"], "interface": r["type"],
        "keyword": r["keyword"], "macro": r["keyword"], "method": r["strong"], "namespace": r["type"],
        "number": r["number"], "parameter": {"foreground": r["text"], "italic": True}, "property": r["prop"],
        "string": r["string"], "struct": r["type"], "type": r["type"], "typeParameter": r["type"],
        "variable": r["text"], "variable.readonly": r["number"], "variable.defaultLibrary": r["keyword"],
    }


def theme(name: str, p: dict, tk: dict) -> dict:
    return {
        "$schema": "vscode://schemas/color-theme", "name": p["title"], "type": "dark",
        "semanticHighlighting": True, "colors": workbench(p, tk),
        "tokenColors": token_colors(p), "semanticTokenColors": semantic(p),
    }


def render(ctx) -> dict:
    base = "apps/vscode/ttox-themes/"
    out: dict = {}
    themes = []
    for name, p in ctx.all_palettes.items():
        rel = f"themes/ttox-{name}-color-theme.json"
        out[base + rel] = json.dumps(theme(name, p, ctx.tokens), indent=2, ensure_ascii=False) + "\n"
        themes.append({"label": p["title"], "uiTheme": "vs-dark", "path": "./" + rel})
    pkg = {
        "name": EXT_NAME, "displayName": "TTox Themes", "publisher": EXT_PUBLISHER, "version": EXT_VERSION,
        "description": "TToxThemes colour themes: " + ", ".join(p["title"] for p in ctx.all_palettes.values()),
        "license": "GPL-3.0-or-later", "engines": {"vscode": "^1.60.0"}, "categories": ["Themes"],
        "keywords": ["theme", "dark", "ttox"], "contributes": {"themes": themes},
    }
    out[base + "package.json"] = json.dumps(pkg, indent=2) + "\n"
    out[base + "README.md"] = (
        "# TTox Themes\n\nGenerated by TToxThemes (`build/targets/apps_vscode.py`); do not edit by hand.\n\n"
        + "".join(f"- {p['title']}\n" for p in ctx.all_palettes.values())
        + "\nSuggested fonts: editor `" + ctx.tokens["font"]["mono"] + "`, fallback `"
        + ctx.tokens["font"]["mono_fallback"] + "`.\n")
    return out
