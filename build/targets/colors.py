"""Runtime colour files consumed by eww, rofi, dunst, shell scripts and the CLI.

dist/core/colors/ttox-<variant>-<mode>/colors.{scss,css,sh,json}
At runtime ~/.config/ttox/current -> that directory.
"""
import json
NAME = "colors"; PACK = "core"

def render(ctx):
    out = {}
    p, t = ctx.p, ctx.tokens
    base = {k: v for k, v in p.items() if isinstance(v, str) and v.startswith("#")}
    for mode, m in sorted(ctx.modes.items()):
        d = f"core/colors/{ctx.slug}-{mode}/"
        glass = {  # ready-made rgba strings for each ladder surface
            "glass_term": ctx.rgba(p["bg"], m["term"]), "glass_body": ctx.rgba(p["surface"], m["body"]),
            "glass_bar": ctx.rgba(p["bg"], m["bar"]), "glass_popup": ctx.rgba(p["raised"], m["popup"]),
            "outline_active": ctx.rgba(p["fg"], t["border"]["active_alpha"]),
            "hairline": ctx.rgba(p["fg"], t["border"]["hairline_alpha"]),
            "wash_select": ctx.rgba(p["accent"], t["wash"]["select_alpha"]),
            "wash_hover": ctx.rgba(p["fg"], t["wash"]["hover_alpha"]),
        }
        allv = dict(base); allv.update(glass)
        scss = [f"// {p['title']} / {mode}: generated, do not edit"]
        scss += [f"${k.replace('_', '-')}: {v};" for k, v in sorted(allv.items())]
        scss += [f"$term-{i}: {c};" for i, c in enumerate(p["term"])]
        scss += [f"$radius-{k}: {v}px;" for k, v in sorted(t["radius"].items())]
        scss += [f"$font-mono: \"{t['font']['mono']}\";", f"$font-ui: \"{t['font']['ui']}\";",
                 f"$blur: {m['blur']}px;", f"$graphs: {'true' if m['graphs'] else 'false'};"]
        css = [":root{"] + [f"  --{k.replace('_', '-')}: {v};" for k, v in sorted(allv.items())] + ["}"]
        sh = [f"# {p['title']} / {mode}"] + [f"TTOX_{k.upper()}='{v}'" for k, v in sorted(allv.items())]
        sh += [f"TTOX_TERM_{i}='{c}'" for i, c in enumerate(p["term"])]
        sh += [f"TTOX_VARIANT='{ctx.name}'", f"TTOX_MODE='{mode}'", f"TTOX_TITLE='{p['title']}'",
               f"TTOX_POLL='{m['poll']}'", f"TTOX_CURSOR='{p['cursor']}'"]
        js = {"variant": ctx.name, "mode": mode, "title": p["title"], "colors": base, "glass": glass,
              "term": p["term"], "mode_tokens": m, "tokens": t}
        out[d + "colors.scss"] = "\n".join(scss) + "\n"
        out[d + "colors.css"] = "\n".join(css) + "\n"
        out[d + "colors.sh"] = "\n".join(sh) + "\n"
        out[d + "colors.json"] = json.dumps(js, indent=1, sort_keys=True) + "\n"
    return out
