"""Build index.html — the shareable map of everything SemiAgency offers — from city/city.json and the repo.

    python scripts/build_city.py            # writes index.html, reports unmapped features
    python scripts/build_city.py --check    # exit 1 if any feature in the repo is not placed on the map

The page is self-contained (no network, no corporate data): it embeds the prompt files, the M365 build
sheets and the docs the manifest names, after applying the manifest's `redact` map. Anything new in
.github/prompts, .github/agents, m365/ or agents/ that no building claims is placed automatically in the
"New Arrivals" district so the map never silently lags the repo. Python 3 standard library only.
"""
import argparse
import base64
import html
import json
import re
import struct
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "city" / "city.json"


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- markdown (small, enough for our docs)

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITAL = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
STRIKE = re.compile(r"~~(.+?)~~")


def inline(s):
    s = html.escape(s, quote=False)
    s = INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", s)
    s = BOLD.sub(r"<b>\1</b>", s)
    s = ITAL.sub(r"<i>\1</i>", s)
    s = STRIKE.sub(r"<s>\1</s>", s)
    s = LINK.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def strip_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        text = text[m.end():]
    return meta, text


def md_to_html(text, shift=2):
    """Headings, paragraphs, fenced code, tables, lists (nested by indent), blockquotes, hr."""
    lines = text.splitlines()
    out, i, n = [], 0, len(lines)
    para = []

    def flush_para():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush_para()
            lang = s[3:].strip()
            j = i + 1
            buf = []
            while j < n and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            code = html.escape("\n".join(buf))
            out.append(f'<div class="code"><button class="copy" type="button">Copy</button>'
                       f'<pre data-lang="{html.escape(lang)}">{code}</pre></div>')
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush_para()
            lvl = min(6, len(m.group(1)) + shift)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            flush_para()
            out.append("<hr>")
            i += 1
            continue
        if s.startswith("|") and i + 1 < n and re.match(r"^\|?\s*:?-{2,}", lines[i + 1].strip()):
            flush_para()
            head = [c.strip() for c in s.strip("|").split("|")]
            rows = []
            j = i + 2
            while j < n and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            t = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            for r in rows:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</tbody></table>")
            i = j
            continue
        lm = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if lm:
            flush_para()
            stack = []  # (indent, tag)
            while i < n:
                lm = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i])
                if not lm:
                    # continuation line of the previous item?
                    if lines[i].strip() and lines[i].startswith(" " * (stack[-1][0] + 2)) and stack:
                        out[-1] = out[-1][:-5] + " " + inline(lines[i].strip()) + "</li>"
                        i += 1
                        continue
                    break
                ind = len(lm.group(1).expandtabs(4))
                tag = "ol" if lm.group(2)[0].isdigit() else "ul"
                item = lm.group(3)
                cb = re.match(r"^\[([ xX])\]\s+(.*)$", item)
                if cb:
                    item = ("☑ " if cb.group(1) != " " else "☐ ") + cb.group(2)
                while stack and ind < stack[-1][0]:
                    out.append(f"</{stack.pop()[1]}>")
                if not stack or ind > stack[-1][0]:
                    stack.append((ind, tag))
                    out.append(f"<{tag}>")
                out.append(f"<li>{inline(item)}</li>")
                i += 1
            while stack:
                out.append(f"</{stack.pop()[1]}>")
            continue
        if s.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue
        if not s:
            flush_para()
            i += 1
            continue
        para.append(s)
        i += 1
    flush_para()
    return "\n".join(out)


# ---------------------------------------------------------------- repo scanning

def load_manifest():
    if not MANIFEST.is_file():
        die(f"missing {MANIFEST.relative_to(ROOT)}")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def redact(text, table):
    for k, v in table.items():
        text = text.replace(k, v)
    return text


def safe_path(rel, never):
    rel = rel.replace("\\", "/")
    for bad in never:
        if rel.startswith(bad):
            die(f"refusing to embed {rel}: under never_embed '{bad}'")
    p = ROOT / rel
    if not p.is_file():
        die(f"manifest names a file that does not exist: {rel}")
    return p


def read(rel, m):
    return redact(safe_path(rel, m["never_embed"]).read_text(encoding="utf-8"), m["redact"])


def prompt_info(name, m):
    rel = f".github/prompts/{name}.prompt.md"
    meta, body = strip_frontmatter(read(rel, m))
    return {"name": name, "file": rel, "description": meta.get("description", ""),
            "body": body.strip()}


def agent_info(name, m):
    rel = f".github/agents/{name}.agent.md"
    meta, body = strip_frontmatter(read(rel, m))
    return {"name": name, "file": rel, "description": meta.get("description", ""), "body": body.strip()}


def doc_info(d, m):
    text = read(d["file"], m)
    _, body = strip_frontmatter(text)
    return {"title": d.get("title", d["file"]), "file": d["file"], "html": md_to_html(body)}


def first_heading(text):
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def scan_features():
    """Everything in the repo that deserves a building: (kind, key, rel path, description)."""
    feats = []
    for p in sorted((ROOT / ".github" / "prompts").glob("*.prompt.md")):
        meta, _ = strip_frontmatter(p.read_text(encoding="utf-8"))
        feats.append(("prompt", p.name[:-len(".prompt.md")], p.relative_to(ROOT).as_posix(), meta.get("description", "")))
    for p in sorted((ROOT / ".github" / "agents").glob("*.agent.md")):
        meta, _ = strip_frontmatter(p.read_text(encoding="utf-8"))
        feats.append(("agent", p.name[:-len(".agent.md")], p.relative_to(ROOT).as_posix(), meta.get("description", "")))
    for p in sorted((ROOT / "m365").glob("[0-9]*.md")):
        feats.append(("sheet", p.relative_to(ROOT).as_posix(), p.relative_to(ROOT).as_posix(),
                      first_heading(p.read_text(encoding="utf-8"))))
    agents_dir = ROOT / "agents"
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            feats.append(("sheet", p.relative_to(ROOT).as_posix(), p.relative_to(ROOT).as_posix(),
                          first_heading(p.read_text(encoding="utf-8"))))
    for p in sorted(ROOT.glob("*/README.md")):
        top = p.parent.name
        if top in ("m365", "docs", "scripts", "brand", "engagements", "tests", "templates", "city", "tracker"):
            continue
        feats.append(("kit", f"{top}/", p.relative_to(ROOT).as_posix(), first_heading(p.read_text(encoding="utf-8"))))
    return feats


def claimed_keys(m):
    keys = set()
    for b in m["buildings"]:
        for p in b.get("prompts", []):
            keys.add(("prompt", p))
        for a in b.get("agents", []):
            keys.add(("agent", a))
        for d in b.get("docs", []):
            keys.add(("sheet", d["file"]))
            keys.add(("kit", d["file"].split("/")[0] + "/"))
    # the analyst agent is the engine behind every D2P prompt; it is implicitly claimed by the Meeting Quarter
    keys.add(("agent", "analyst"))
    return keys


# ---------------------------------------------------------------- scene (illustrated mode)

def image_size(data):
    """(width, height) of a PNG or JPEG from its bytes; stdlib only."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seglen = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + seglen
    die("scene image must be PNG or JPEG")


def load_scene(m, link_image=False):
    """city/scene.png|jpg + city/hotspots.json → dict for the page, or None (drawn-city fallback)."""
    cdir = ROOT / "city"
    img = next((p for ext in ("png", "jpg", "jpeg") for p in [cdir / f"scene.{ext}"] if p.is_file()), None)
    hs = cdir / "hotspots.json"
    if not img and not hs.is_file():
        return None
    if not img:
        die("city/hotspots.json exists but no city/scene.png|jpg")
    if not hs.is_file():
        die(f"{img.name} exists but no city/hotspots.json — trace the buildings with city/hotspot-editor.html")
    data = img.read_bytes()
    w, h = image_size(data)
    spots = json.loads(hs.read_text(encoding="utf-8"))["hotspots"]
    ids = [x["id"] for x in spots]
    if len(ids) != len(set(ids)):
        die("duplicate hotspot ids in city/hotspots.json")
    for x in spots:
        if len(x.get("points", [])) < 3:
            die(f"hotspot {x['id']} has fewer than 3 points")
    mime = "image/png" if img.suffix == ".png" else "image/jpeg"
    src = ("city/" + img.name) if link_image else f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
    return {"src": src, "w": w, "h": h, "hotspots": spots, "file": img.name, "bytes": len(data)}


def assign_hotspots(buildings, scene, landmarks=()):
    """Buildings and landmarks name their hotspot in city.json; unmapped (auto) buildings take free hotspots
    automatically. Returns the list of hotspot ids left free (= free lots)."""
    if not scene:
        return []
    by_id = {x["id"]: x for x in scene["hotspots"]}
    used = set()
    for lm in landmarks:
        if lm["hotspot"] not in by_id:
            die(f"landmark '{lm['name']}' names hotspot '{lm['hotspot']}' which is not in city/hotspots.json")
        if lm["hotspot"] in used:
            die(f"hotspot '{lm['hotspot']}' is used by two landmarks")
        used.add(lm["hotspot"])
    for b in buildings:
        hid = b.get("hotspot")
        if hid:
            if hid not in by_id:
                die(f"building {b['id']} names hotspot '{hid}' which is not in city/hotspots.json")
            if hid in used:
                die(f"hotspot '{hid}' is used by two buildings")
            used.add(hid)
    free = [x["id"] for x in scene["hotspots"] if x["id"] not in used]
    for b in buildings:
        if not b.get("hotspot"):
            if not free:
                print(f"warning: no free hotspot left for {b['id']}; it will only be reachable from the wayfinder/list")
                continue
            b["hotspot"] = free.pop(0)
            b["hotspot_auto"] = True
    return free


# ---------------------------------------------------------------- assembling

def build_data(m, link_image=False):
    claimed = claimed_keys(m)
    unmapped = [f for f in scan_features() if (f[0], f[1]) not in claimed]
    buildings = []
    for b in m["buildings"]:
        d = dict(b)
        d["prompts"] = [prompt_info(p, m) for p in b.get("prompts", [])]
        d["agents"] = [agent_info(a, m) for a in b.get("agents", [])]
        d["docs"] = [doc_info(x, m) for x in b.get("docs", [])]
        d["steps"] = [{"say": md_inline(s.get("say", "")), "copy": s.get("copy", "")} for s in b.get("steps", [])]
        buildings.append(d)
    for kind, key, rel, desc in unmapped:
        bid = "new-" + re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
        d = {"id": bid, "district": "arrivals", "name": key if kind != "sheet" else Path(rel).stem,
             "shape": "construction", "audience": "everyone", "auto": True,
             "pitch": desc or "New in the repo — nobody has described it yet.",
             "steps": [], "prompts": [], "agents": [], "docs": [],
             "source": rel, "kind": kind}
        if kind == "prompt":
            d["prompts"] = [prompt_info(key, m)]
            d["steps"] = [{"say": "Copilot Chat, agent mode:", "copy": f"/{key}"}]
        elif kind == "agent":
            d["agents"] = [agent_info(key, m)]
            d["steps"] = [{"say": "Copilot Chat, agent mode:", "copy": f"@{key}"}]
        elif kind in ("sheet", "kit"):
            d["docs"] = [doc_info({"file": rel, "title": rel}, m)]
        buildings.append(d)
    data = {k: m[k] for k in ("title", "tagline", "audiences", "districts", "lots_per_district", "journeys")}
    data["modes"] = m.get("modes", {})
    data["landmarks"] = m.get("landmarks", [])
    data["area_label_at"] = m.get("area_label_at", {})
    for d in buildings:
        d["asks"] = [dict(a, when=a.get("when", ""), get=a.get("get", "")) for a in d.get("asks", [])]
    data["buildings"] = buildings
    data["built"] = date.today().isoformat()
    scene = load_scene(m, link_image)
    data["free_lots"] = assign_hotspots(buildings, scene, data["landmarks"] if scene else ())
    data["scene"] = scene
    return data, unmapped


def md_inline(s):
    return inline(s)


# ---------------------------------------------------------------- page

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--sky1:#bfe3ff;--sky2:#eaf6ff;--ground:#cfe6c4;--road:#e9eef2;--ink:#1d2733;--mut:#5b6773;--card:#fff;--line:#d6dee6;--acc:#1f6fd0;--acc2:#e9f1fb;--ok:#2a8a3a}
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:linear-gradient(var(--sky1),var(--sky2) 45%,var(--ground) 45.01%)}
header{padding:14px 20px 6px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
header h1{font-size:22px;margin:0;letter-spacing:.2px}
header .tag{color:var(--mut);flex-basis:100%;margin-top:-4px}
.bar{display:flex;flex-wrap:wrap;gap:8px;padding:6px 20px 8px;align-items:center}
.bar .lbl{color:var(--mut);font-size:13px;margin-right:2px}
button.chip,a.chip{font:inherit;font-size:13px;border:1px solid var(--line);background:#fff;border-radius:999px;padding:4px 12px;cursor:pointer;color:var(--ink);text-decoration:none}
button.chip.on{background:var(--acc);color:#fff;border-color:var(--acc)}
button.chip.tour{background:#fff8e1;border-color:#e6c76b}
#cityWrap{position:relative;margin:0 auto;max-width:1440px;padding:0 8px}
svg#city{width:100%;height:auto;display:block}
.bld{cursor:pointer}
.bld .body{transition:opacity .2s}
.bld.dim{opacity:.35}
polygon.hs{fill:rgba(255,255,255,0);stroke:rgba(255,255,255,0);stroke-width:3;stroke-linejoin:round;transition:fill .15s,stroke .15s;vector-effect:non-scaling-stroke}
.bld:hover polygon.hs,.bld.focus polygon.hs{fill:rgba(255,190,40,.22);stroke:#ffb400}
polygon.lot{fill:rgba(255,255,255,0);stroke:rgba(255,255,255,.0);stroke-dasharray:6 5;stroke-width:2}
#city.lots polygon.lot{stroke:rgba(30,60,90,.45);fill:rgba(255,255,255,.12)}
.pill{font-size:12px;fill:#1d2733}
.pillbg{fill:rgba(255,255,255,.88);stroke:rgba(0,0,0,.12)}
.bld.dim .pill,.bld.dim .pillbg{opacity:.4}
#city.nolabels .pill,#city.nolabels .pillbg{display:none}
#city.scene .bld{cursor:pointer}
.bld:hover .glow,.bld.focus .glow{opacity:1}
.glow{opacity:0;fill:none;stroke:#ffb400;stroke-width:4;stroke-linejoin:round;filter:url(#soft)}
.bld text{font-size:11.5px;fill:var(--ink);text-anchor:middle;pointer-events:none;paint-order:stroke;stroke:#fff;stroke-width:2.5px;stroke-linejoin:round}
.dname{font-size:16px;font-weight:600;fill:var(--ink)}
.dsub{font-size:12px;fill:var(--mut)}
.tick{fill:var(--ok)}
#tip{position:absolute;pointer-events:none;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px 10px;max-width:280px;font-size:13px;box-shadow:0 6px 20px rgba(0,0,0,.12);display:none;z-index:5}
#tip b{display:block;margin-bottom:2px}
#guide{position:absolute;right:16px;top:12px;background:rgba(255,252,240,.97);border:1px solid #e6c76b;border-radius:12px;padding:12px 14px 12px 16px;width:min(380px,calc(100% - 40px));max-height:calc(100% - 24px);overflow:auto;box-shadow:0 8px 24px rgba(0,0,0,.18);display:none;z-index:6}
#guide .x{position:absolute;right:8px;top:4px;border:0;background:transparent;font-size:22px;cursor:pointer;color:var(--mut)}
#guide .who{font-weight:700;font-size:15px;margin:0 22px 4px 0}
#guide .when{font-size:13px;color:#4a4436;margin-bottom:8px}
#guide .when b{color:var(--ink)}
#guide ol{margin:0;padding-left:22px;font-size:13px}
#guide li{margin:4px 0;cursor:pointer;padding:3px 6px;border-radius:6px}
#guide li.cur{background:#ffe9a8}
#guide li b{display:block}
#guide .nav{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
#guide .nav .sp{flex:1}
.badge circle{fill:#1f6fd0;stroke:#fff;stroke-width:2}
.badge text{fill:#fff;font-weight:700;text-anchor:middle;stroke:none}
#path{fill:none;stroke:#1f6fd0;stroke-width:3;stroke-dasharray:9 7;opacity:.85;pointer-events:none}
.bld.focus polygon.hs{fill:rgba(31,111,208,.20);stroke:#1f6fd0}
.bld.cur polygon.hs{fill:rgba(255,190,40,.30);stroke:#ffb400}
button.chip.sel{background:#fff3c4;border-color:#e6c76b;font-weight:600}
@media(max-width:900px){#guide{position:static;width:auto;max-height:none;margin:8px 0}}
.cloud{animation:drift linear infinite}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(1500px)}}
@media(prefers-reduced-motion:reduce){.cloud{animation:none}}
/* modal */
#ov{position:fixed;inset:0;background:rgba(20,30,40,.45);display:none;z-index:20;overflow:auto;padding:24px 12px}
#ov.on{display:block}
.modal{background:var(--card);max-width:860px;margin:0 auto;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,.3);padding:22px 26px 26px;position:relative}
.modal .x{position:absolute;right:12px;top:10px;border:0;background:transparent;font-size:26px;cursor:pointer;color:var(--mut);line-height:1}
.modal h2{margin:0 0 2px;font-size:22px}
.modal .meta{color:var(--mut);font-size:13px;margin-bottom:12px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.modal .aud{border:1px solid var(--line);border-radius:999px;padding:1px 9px;font-size:12px;background:var(--acc2)}
.modal .pitch{font-size:16px;margin:0 0 16px}
.modal h3{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:22px 0 8px}
.step{margin:8px 0}
.step .say{margin:0 0 4px}
.code{position:relative;margin:4px 0 10px}
.code pre{margin:0;background:#f4f7fa;border:1px solid var(--line);border-radius:8px;padding:10px 84px 10px 12px;overflow:auto;font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap;word-break:break-word}
.code .copy{position:absolute;right:8px;top:8px;font:12px system-ui;border:1px solid var(--line);background:#fff;border-radius:6px;padding:3px 9px;cursor:pointer}
.code .copy.done{background:var(--ok);color:#fff;border-color:var(--ok)}
details{border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:8px 0;background:#fbfcfd}
details summary{cursor:pointer;font-weight:600}
details .desc{color:var(--mut);font-size:13px;margin:2px 0 6px}
.doc{font-size:14px}.doc h3,.doc h4,.doc h5,.doc h6{text-transform:none;letter-spacing:0;color:var(--ink);margin:16px 0 6px}
.doc h3{font-size:17px}.doc h4{font-size:15px}
.doc table{border-collapse:collapse;margin:8px 0;font-size:13px;display:block;overflow:auto}
.doc th,.doc td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
.doc code,.step code,.pitch code{background:#f0f3f6;border-radius:4px;padding:0 4px;font-size:.92em}
.doc blockquote{border-left:3px solid var(--line);margin:8px 0;padding:2px 12px;color:var(--mut)}
.modal .src{color:var(--mut);font-size:12px;margin-top:18px}
footer{color:var(--mut);font-size:12px;text-align:center;padding:16px}
kbd{border:1px solid var(--line);border-radius:4px;padding:0 5px;font-size:12px;background:#fff}
@media(max-width:700px){.modal{padding:16px 14px}.bld text{font-size:14px}}
/* v2: areas, landmarks, modes, asks, front desk */
button.chip .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:0}
button.chip[hidden]{display:none}
.bld polygon.hs{stroke:color-mix(in srgb,var(--ac,#ffb400) 55%,transparent);stroke-width:1.6}
.bld:hover polygon.hs{stroke-width:3}
.bld:hover polygon.hs{fill:color-mix(in srgb,var(--ac,#ffb400) 28%,transparent);stroke:var(--ac,#ffb400)}
#city.areas .bld polygon.hs{fill:color-mix(in srgb,var(--ac) 38%,transparent);stroke:color-mix(in srgb,var(--ac) 80%,#fff)}
.bld.focus polygon.hs{fill:color-mix(in srgb,var(--ac,#1f6fd0) 30%,transparent);stroke:var(--ac,#1f6fd0);stroke-width:3.5}
.bld .pill,.bld .pillbg{display:none}
#city.alllabels .bld .pill,#city.alllabels .bld .pillbg,.bld.focus .pill,.bld.focus .pillbg,.bld:hover .pill,.bld:hover .pillbg{display:inline}
#city.nolabels .apill,#city.nolabels .apillbg,#city.nolabels .lm .pill,#city.nolabels .lm .pillbg{display:none}
#city.picked .apill,#city.picked .apillbg{opacity:.35}
.apillbg{stroke:#fff;stroke-width:1.5;opacity:.93}
.apill{fill:#fff;font-weight:700;pointer-events:none}
.area-hit{cursor:pointer}
.lm{cursor:pointer}
.lm polygon{fill:rgba(255,255,255,0);stroke:rgba(255,255,255,0);stroke-width:2.5;stroke-dasharray:6 4;vector-effect:non-scaling-stroke}
.lm:hover polygon,.lm.on polygon{fill:rgba(58,154,110,.22);stroke:#3a9a6e}
.lm .pillbg{fill:rgba(58,154,110,.92);stroke:#fff}
.lm .pill{fill:#fff;font-weight:600}
.modal .areabar{height:6px;border-radius:6px 6px 0 0;margin:-22px -26px 16px}
.modal .sub{font-size:14px;color:var(--mut);margin:2px 0 8px}
.mode{border-radius:999px;padding:1px 9px;font-size:12px;font-weight:600;background:#eef2f6;border:1px solid var(--line)}
.mode.auto{background:#e3f4ea;border-color:#9fd1b3}.mode.click{background:#e9f1fb;border-color:#a9c6ea}.mode.setup{background:#fdf0dd;border-color:#e8c48e}
table.asks{border-collapse:collapse;width:100%;font-size:13px;margin:4px 0 8px}
table.asks th{font-size:12px;text-align:left;color:var(--mut);font-weight:600;padding:4px 8px;border-bottom:1px solid var(--line)}
table.asks td{padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
table.asks td.say{width:46%}
table.asks .code{margin:0}
table.asks .code pre{padding:6px 60px 6px 8px}
table.asks tr.hi td{background:#fff7d6}
table.asks tr.lo td{opacity:.5}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;margin:8px 0 4px}
.card{border:1px solid var(--line);border-left:6px solid var(--ac);border-radius:10px;padding:10px 12px;background:#fff;display:flex;flex-direction:column;gap:4px}
.card h4{margin:0;font-size:15px}
.card .k{font-size:12px;color:var(--mut)}
.card .v{font-size:13px}
.card button{align-self:flex-start;margin-top:4px}
.grp{font-size:13px;font-weight:700;margin:14px 0 2px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em}
#guide .facts{font-size:12.5px;margin:0 0 8px;display:grid;grid-template-columns:auto 1fr;gap:2px 8px}
#guide .facts b{color:var(--mut);font-weight:600}
#guide{border-left:6px solid var(--gac,#e6c76b)}
#guide.left{right:auto;left:16px}
</style></head><body>
<header>
  <h1>__TITLE__</h1>
  <div class="tag">__TAGLINE__</div>
</header>
<div class="bar" id="who"><span class="lbl">I work in</span></div>
<div class="bar" id="way"><span class="lbl">I want to…</span></div>
<div class="bar" id="aud"><span class="lbl">Areas</span></div>
<div id="cityWrap">
  <svg id="city" xmlns="http://www.w3.org/2000/svg"></svg>
  <div id="tip"></div>
  <div id="guide"><button class="x" id="gClose" aria-label="Clear selection">×</button><div class="who"></div><div class="when"></div><div class="facts"></div><ol class="stops"></ol><div class="nav"><button class="chip" id="gPrev">‹ Previous stop</button><button class="chip" id="gNext">Next stop ›</button><span class="sp"></span><button class="chip" id="gOpen">Open this building</button></div></div>
</div>
<footer>Generated from the SemiAgency repo on __BUILT__ by <code>scripts/build_city.py</code>. Pick what you want to do to see its steps numbered on the map; click an area's name to see what lives there. Press <kbd>Esc</kbd> to close a building.</footer>
<div id="ov"><div class="modal" role="dialog" aria-modal="true"><button class="x" id="mx" aria-label="Close">×</button><div id="mc"></div></div></div>
<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---------- building shapes: each returns SVG markup for a building of width w, height h with its base at (0,0) going up (negative y) */
const win = (w,h,cols,rows,top=14,side=9)=>{ let s=''; const cw=(w-2*side)/cols, rh=(h-top-12)/rows; for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){ s+=`<rect x="${side+c*cw+cw*0.2}" y="${-h+top+r*rh+rh*0.2}" width="${cw*0.6}" height="${rh*0.55}" fill="#fff8d6" opacity=".9"/>`;} return s; };
const SHAPES = {
  hall:(w,h)=>`<rect x="0" y="${-h+22}" width="${w}" height="${h-22}" fill="#f2f4f7" stroke="#8f9bad"/><polygon points="-6,${-h+22} ${w/2},${-h} ${w+6},${-h+22}" fill="#8fa3c4" stroke="#6b7d9b"/>${win(w,h-22,3,2,8)}<rect x="${w/2-8}" y="-22" width="16" height="22" fill="#6b7d9b"/><circle cx="${w/2}" cy="${-h-8}" r="3" fill="#e9b949"/><line x1="${w/2}" y1="${-h}" x2="${w/2}" y2="${-h-6}" stroke="#6b7d9b"/>`,
  columns:(w,h)=>`<rect x="0" y="${-h+16}" width="${w}" height="${h-16}" fill="#f7f1e3" stroke="#a89f8a"/><polygon points="-5,${-h+16} ${w/2},${-h} ${w+5},${-h+16}" fill="#d9cdb0" stroke="#a89f8a"/>${[0.15,0.38,0.62,0.85].map(f=>`<rect x="${w*f-3}" y="${-h+20}" width="6" height="${h-26}" fill="#e6dcc3" stroke="#a89f8a"/>`).join('')}<rect x="0" y="-6" width="${w}" height="6" fill="#d9cdb0"/>`,
  studio:(w,h)=>`<rect x="0" y="${-h}" width="${w}" height="${h}" fill="#fff" stroke="#8f9bad"/><rect x="4" y="${-h+4}" width="${w-8}" height="${h*0.45}" fill="#bfe3ff" opacity=".9"/><rect x="0" y="${-h}" width="${w}" height="6" fill="#4a5f7a"/>${win(w,h*0.5,2,1,4)}<rect x="${w*0.3}" y="-18" width="${w*0.4}" height="18" fill="#4a5f7a"/>`,
  factory:(w,h)=>`<rect x="0" y="${-h*0.7}" width="${w}" height="${h*0.7}" fill="#dde3ea" stroke="#8f9bad"/><polygon points="0,${-h*0.7} ${w*0.33},${-h*0.85} ${w*0.33},${-h*0.7} ${w*0.66},${-h*0.85} ${w*0.66},${-h*0.7} ${w},${-h*0.85} ${w},${-h*0.7}" fill="#8fa3c4" stroke="#6b7d9b"/><rect x="${w*0.72}" y="${-h}" width="10" height="${h*0.3}" fill="#6b7d9b"/><rect x="6" y="${-h*0.5}" width="${w-12}" height="${h*0.25}" fill="#fff8d6"/>`,
  dome:(w,h)=>`<rect x="0" y="${-h*0.55}" width="${w}" height="${h*0.55}" fill="#f6efe9" stroke="#a89f8a"/><path d="M0 ${-h*0.55} A ${w/2} ${h*0.5} 0 0 1 ${w} ${-h*0.55} Z" fill="#c9a26b" stroke="#a07f4d"/><rect x="${w/2-2}" y="${-h}" width="4" height="${h*0.06}" fill="#a07f4d"/>${win(w,h*0.55,3,1,6)}`,
  warehouse:(w,h)=>`<rect x="0" y="${-h*0.75}" width="${w}" height="${h*0.75}" fill="#e6d9c8" stroke="#a89f8a"/><path d="M-3 ${-h*0.75} Q ${w/2} ${-h-6} ${w+3} ${-h*0.75} Z" fill="#b48a5a" stroke="#8c6a42"/><rect x="${w*0.2}" y="${-h*0.45}" width="${w*0.6}" height="${h*0.45}" fill="#8c6a42"/><rect x="${w*0.25}" y="${-h*0.4}" width="${w*0.5}" height="${h*0.4}" fill="#6f5334"/>`,
  house:(w,h)=>`<rect x="0" y="${-h*0.62}" width="${w}" height="${h*0.62}" fill="#fff5ea" stroke="#a89f8a"/><polygon points="-4,${-h*0.62} ${w/2},${-h} ${w+4},${-h*0.62}" fill="#d96f5a" stroke="#a84a3a"/><rect x="${w*0.4}" y="${-h*0.3}" width="${w*0.2}" height="${h*0.3}" fill="#6f5334"/><rect x="${w*0.1}" y="${-h*0.5}" width="${w*0.2}" height="${h*0.15}" fill="#fff8d6"/><rect x="${w*0.7}" y="${-h*0.5}" width="${w*0.2}" height="${h*0.15}" fill="#fff8d6"/>`,
  tower:(w,h)=>`<rect x="${w*0.3}" y="${-h*0.55}" width="${w*0.4}" height="${h*0.55}" fill="#e3e8ee" stroke="#8f9bad"/><polygon points="${w*0.3},${-h*0.55} ${w/2},${-h} ${w*0.7},${-h*0.55}" fill="none" stroke="#6b7d9b" stroke-width="2"/><line x1="${w/2}" y1="${-h*0.55}" x2="${w/2}" y2="${-h}" stroke="#6b7d9b" stroke-width="2"/><line x1="${w*0.36}" y1="${-h*0.7}" x2="${w*0.64}" y2="${-h*0.7}" stroke="#6b7d9b"/><line x1="${w*0.42}" y1="${-h*0.85}" x2="${w*0.58}" y2="${-h*0.85}" stroke="#6b7d9b"/><circle cx="${w/2}" cy="${-h-3}" r="3" fill="#e0504a"/><path d="M${w/2-12} ${-h-2} q 12 -12 24 0" fill="none" stroke="#e0504a" opacity=".7"/>${win(w*0.4,h*0.55,1,3,6,6).replace(/x="([\d.]+)"/g,(m,x)=>`x="${+x+w*0.3}"`)}`,
  office:(w,h)=>`<rect x="0" y="${-h}" width="${w}" height="${h}" fill="#dfe9f5" stroke="#8f9bad"/>${win(w,h,3,4,8)}<rect x="0" y="${-h}" width="${w}" height="5" fill="#4a5f7a"/>`,
  lighthouse:(w,h)=>`<polygon points="${w*0.3},0 ${w*0.7},0 ${w*0.62},${-h*0.7} ${w*0.38},${-h*0.7}" fill="#fff" stroke="#8f9bad"/><polygon points="${w*0.3},0 ${w*0.7},0 ${w*0.68},${-h*0.15} ${w*0.32},${-h*0.15}" fill="#e0504a"/><polygon points="${w*0.35},${-h*0.35} ${w*0.65},${-h*0.35} ${w*0.64},${-h*0.5} ${w*0.36},${-h*0.5}" fill="#e0504a"/><rect x="${w*0.34}" y="${-h*0.88}" width="${w*0.32}" height="${h*0.18}" fill="#fff8d6" stroke="#8f9bad"/><polygon points="${w*0.3},${-h*0.88} ${w/2},${-h} ${w*0.7},${-h*0.88}" fill="#4a5f7a"/>`,
  clock:(w,h)=>`<rect x="${w*0.25}" y="${-h*0.8}" width="${w*0.5}" height="${h*0.8}" fill="#f2e7d5" stroke="#a89f8a"/><polygon points="${w*0.2},${-h*0.8} ${w/2},${-h} ${w*0.8},${-h*0.8}" fill="#6d8f6a" stroke="#4e6b4b"/><circle cx="${w/2}" cy="${-h*0.62}" r="${w*0.16}" fill="#fff" stroke="#4e6b4b"/><line x1="${w/2}" y1="${-h*0.62}" x2="${w/2}" y2="${-h*0.62-w*0.11}" stroke="#4e6b4b" stroke-width="2"/><line x1="${w/2}" y1="${-h*0.62}" x2="${w/2+w*0.08}" y2="${-h*0.62}" stroke="#4e6b4b" stroke-width="2"/><rect x="${w*0.42}" y="${-h*0.25}" width="${w*0.16}" height="${h*0.25}" fill="#6f5334"/>`,
  embassy:(w,h)=>`<rect x="0" y="${-h*0.7}" width="${w}" height="${h*0.7}" fill="#f8f4ec" stroke="#a89f8a"/><rect x="0" y="${-h*0.7}" width="${w}" height="6" fill="#a89f8a"/>${win(w,h*0.7,3,2,10)}<line x1="${w*0.15}" y1="${-h*0.7}" x2="${w*0.15}" y2="${-h}" stroke="#6b7d9b" stroke-width="2"/><polygon points="${w*0.15},${-h} ${w*0.15+18},${-h+5} ${w*0.15},${-h+10}" fill="#1f6fd0"/><rect x="${w*0.4}" y="${-h*0.3}" width="${w*0.2}" height="${h*0.3}" fill="#4a5f7a"/>`,
  observatory:(w,h)=>`<rect x="${w*0.15}" y="${-h*0.55}" width="${w*0.7}" height="${h*0.55}" fill="#e9e4f2" stroke="#8a7ea6"/><path d="M${w*0.15} ${-h*0.55} A ${w*0.35} ${h*0.4} 0 0 1 ${w*0.85} ${-h*0.55} Z" fill="#b9aee0" stroke="#8a7ea6"/><path d="M${w*0.5} ${-h*0.6} L ${w*0.78} ${-h-2}" stroke="#4a3f6b" stroke-width="5" stroke-linecap="round"/>${win(w*0.7,h*0.55,2,1,6).replace(/x="([\d.]+)"/g,(m,x)=>`x="${+x+w*0.15}"`)}`,
  workshop:(w,h)=>`<rect x="0" y="${-h*0.65}" width="${w}" height="${h*0.65}" fill="#f0e6d6" stroke="#a89f8a"/><polygon points="-3,${-h*0.65} ${w*0.5},${-h*0.85} ${w+3},${-h*0.65}" fill="#c0a27a" stroke="#8c6a42"/><rect x="${w*0.7}" y="${-h}" width="8" height="${h*0.25}" fill="#8c6a42"/><rect x="${w*0.12}" y="${-h*0.5}" width="${w*0.35}" height="${h*0.2}" fill="#fff8d6"/><rect x="${w*0.6}" y="${-h*0.35}" width="${w*0.28}" height="${h*0.35}" fill="#6f5334"/>`,
  small:(w,h)=>`<rect x="${w*0.15}" y="${-h}" width="${w*0.7}" height="${h}" fill="#fff" stroke="#8f9bad"/><rect x="${w*0.15}" y="${-h}" width="${w*0.7}" height="5" fill="#4a5f7a"/>${win(w*0.7,h,2,2,8,6).replace(/x="([\d.]+)"/g,(m,x)=>`x="${+x+w*0.15}"`)}`,
  construction:(w,h)=>`<rect x="0" y="${-h*0.5}" width="${w}" height="${h*0.5}" fill="none" stroke="#c9a26b" stroke-dasharray="5 4" stroke-width="2"/><line x1="${w*0.5}" y1="${-h*0.5}" x2="${w*0.5}" y2="${-h}" stroke="#e9b949" stroke-width="4"/><line x1="${w*0.5}" y1="${-h}" x2="${w+14}" y2="${-h}" stroke="#e9b949" stroke-width="4"/><line x1="${w+8}" y1="${-h}" x2="${w+8}" y2="${-h*0.7}" stroke="#7a7a7a" stroke-width="1.5"/><rect x="${w+3}" y="${-h*0.7}" width="10" height="8" fill="#7a7a7a"/><rect x="4" y="${-h*0.25}" width="${w-8}" height="${h*0.25}" fill="#f2e7d5" stroke="#c9a26b"/>`,
  lot:(w,h)=>`<rect x="0" y="-8" width="${w}" height="8" rx="3" fill="#bcd6ae" stroke="#9fbf90" stroke-dasharray="4 3"/><circle cx="${w*0.3}" cy="-16" r="7" fill="#7fb36e"/><circle cx="${w*0.65}" cy="-20" r="9" fill="#6aa35a"/>`
};
const HEIGHTS = {hall:110,columns:95,studio:100,factory:105,dome:110,warehouse:95,house:85,tower:130,office:125,lighthouse:130,clock:135,embassy:105,observatory:110,workshop:95,small:80,construction:90,lot:30};

/* ---------- layout */
const W = 1440, BW = 62, GAP = 22;
const rowsPlan = DATA.rows || [["agora","proposal","deck","record"],["harbour","idea","lab","yard","arrivals"]];
function layout(){
  const byD = {}; DATA.buildings.forEach(b => (byD[b.district] = byD[b.district] || []).push(b));
  const slots = d => (byD[d]||[]).length + (DATA.lots_per_district[d]||0);
  const rows = rowsPlan.map(r => r.filter(d => DATA.districts.some(x => x.id===d) && (d!=="arrivals" || (byD[d]||[]).length)));
  const pos = {}; let y = 250; const ROWH = 250;
  rows.forEach(row => {
    const total = row.reduce((s,d)=>s+slots(d),0);
    const usable = W - 40 - GAP*(row.length-1);
    let x = 20;
    row.forEach(d => {
      const wd = Math.max(220, usable * slots(d)/total);
      pos[d] = {x, y, w: wd, h: ROWH-20};
      x += wd + GAP;
    });
    // normalise widths if min-width pushed over
    const over = x - GAP - (W-20); if (over > 0) row.forEach(d => { pos[d].w -= over/row.length; }); let xx=20; row.forEach(d=>{pos[d].x=xx; xx+=pos[d].w+GAP;});
    y += ROWH;
  });
  return {pos, byD, height: y + 10};
}

function renderScene(){
  const sc = DATA.scene, svg = $('#city'); svg.classList.add('scene'); if (showLots) svg.classList.add('lots'); if (!showLabels) svg.classList.add('nolabels');
  svg.setAttribute('viewBox', `0 0 ${sc.w} ${sc.h}`);
  const cen = pts => { let x=0,y=0; pts.forEach(p=>{x+=p[0];y+=p[1];}); return [x/pts.length, y/pts.length]; };
  const top = pts => Math.min(...pts.map(p=>p[1]));
  const bot = pts => Math.max(...pts.map(p=>p[1]));
  let s = `<defs><filter id="soft"><feGaussianBlur stdDeviation="2"/></filter></defs><image href="${sc.src}" x="0" y="0" width="${sc.w}" height="${sc.h}"/>`;
  const byId = {}; sc.hotspots.forEach(h => byId[h.id] = h);
  const k = sc.w / 1440; // scale text with the image
  const pts = h => h.points.map(p=>p.join(',')).join(' ');
  const pill = (x, y, text, fs, cls='pill', bg='pillbg', fill='') => { const pw = (text.length*fs*(cls==='apill'?0.64:0.58)+fs*1.4); return `<rect class="${bg}" x="${x-pw/2}" y="${y}" width="${pw}" height="${fs*1.6}" rx="${fs*0.8}" ${fill?`style="fill:${fill}"`:''}/><text class="${cls}" x="${x}" y="${y+fs*1.12}" style="font-size:${fs}px;text-anchor:middle">${esc(text)}</text>`; };
  DATA.free_lots.forEach(id => { const h = byId[id]; s += `<polygon class="lot" data-lot="${id}" points="${pts(h)}"><title>Free lot — a future feature will live here</title></polygon>`; });
  (DATA.landmarks||[]).forEach(lm => { const h = byId[lm.hotspot]; if (!h) return; const c = cen(h.points);
    s += `<g class="lm" data-journey="${lm.journey}"><polygon points="${pts(h)}"><title>${esc(lm.name)} — show this route</title></polygon>${pill(c[0], bot(h.points)-6*k, lm.name.replace('Pier · ',''), 11.5*k)}</g>`; });
  DATA.buildings.forEach(b => { const h = byId[b.hotspot]; if (!h) return; const c = cen(h.points); b._x = c[0]; b._y = top(h.points); b._c = c;
    const ac = (DATA.districts.find(d=>d.id===b.district)||{}).color || '#ffb400';
    s += `<g class="bld" data-id="${b.id}" data-aud="${b.audience}" style="--ac:${ac}"><polygon class="hs" points="${pts(h)}"/>`;
    s += pill(c[0], bot(h.points) + 4*k, b.name, 12*k) + `</g>`; });
  // one name label per area, at the centre of its buildings
  DATA.districts.forEach(d => { const bs = DATA.buildings.filter(b => b.district===d.id && b._c && !b.auto); if (!bs.length) return;
    let x = bs.reduce((a,b)=>a+b._c[0],0)/bs.length, y = Math.min(...bs.map(b=>b._y)) - 30*k; if (bs.length > 3) y = bs.reduce((a,b)=>a+b._c[1],0)/bs.length - 10*k;
    const ov = (DATA.area_label_at||{})[d.id]; if (ov) { x = ov[0]; y = ov[1]; }
    s += `<g class="area-hit" data-district="${d.id}">${pill(x, Math.max(4, y), d.name, 14*k, 'apill', 'apillbg', d.color)}</g>`; });
  s += `<polyline id="path" points=""/><g id="badges"></g>`;
  svg.innerHTML = s;
  svg.querySelectorAll('.bld').forEach(g => { g.addEventListener('click', () => openB(g.dataset.id)); g.addEventListener('mousemove', e => tip(e, g.dataset.id)); g.addEventListener('mouseleave', () => $('#tip').style.display='none'); });
  svg.querySelectorAll('.lm').forEach(g => g.addEventListener('click', () => select({type:'journey', id:g.dataset.journey})));
  svg.querySelectorAll('.area-hit').forEach(g => g.addEventListener('click', () => select({type:'district', id:g.dataset.district})));
  applyFilter(); applySelection();
}
let showLots = false, showLabels = true;
function render(){
  if (DATA.scene) return renderScene();
  const {pos, byD, height} = layout();
  const svg = $('#city'); svg.setAttribute('viewBox', `0 0 ${W} ${height}`);
  let s = `<defs><filter id="soft"><feGaussianBlur stdDeviation="2"/></filter><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fd3ff"/><stop offset="1" stop-color="#eaf6ff"/></linearGradient></defs>`;
  s += `<rect x="0" y="0" width="${W}" height="${height}" fill="url(#sky)"/>`;
  s += `<circle cx="1290" cy="80" r="38" fill="#ffe27a"/><circle cx="1290" cy="80" r="52" fill="#ffe27a" opacity=".25"/>`;
  [[-300,60,1],[-900,110,0.8],[-1500,40,1.2]].forEach(([x,y,k],i)=>{ s += `<g class="cloud" style="animation-duration:${140+i*40}s;animation-delay:${-i*50}s"><g transform="translate(${x},${y}) scale(${k})"><ellipse cx="0" cy="0" rx="46" ry="16" fill="#fff" opacity=".9"/><ellipse cx="-28" cy="6" rx="30" ry="12" fill="#fff" opacity=".9"/><ellipse cx="30" cy="6" rx="34" ry="13" fill="#fff" opacity=".9"/></g></g>`; });
  // distant skyline
  s += `<g opacity=".18" fill="#4a5f7a">` + Array.from({length:26},(_,i)=>{const w=30+((i*37)%40), h=60+((i*53)%140), x=i*56; return `<rect x="${x}" y="${240-h}" width="${w}" height="${h}"/>`;}).join('') + `</g>`;
  s += `<rect x="0" y="238" width="${W}" height="${height-238}" fill="#cfe6c4"/>`;
  s += `<rect x="0" y="236" width="${W}" height="6" fill="#a9c99a"/>`;
  Object.entries(pos).forEach(([d,p])=>{
    const dd = DATA.districts.find(x=>x.id===d);
    s += `<g class="district" data-d="${d}"><rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" rx="14" fill="${dd.color}" stroke="#ffffff" stroke-width="3"/>`;
    s += `<rect x="${p.x+12}" y="${p.y+p.h-16}" width="${p.w-24}" height="10" rx="5" fill="#e9eef2"/><line x1="${p.x+18}" y1="${p.y+p.h-11}" x2="${p.x+p.w-18}" y2="${p.y+p.h-11}" stroke="#fff" stroke-dasharray="10 8" stroke-width="2"/>`;
    s += `<text class="dname" x="${p.x+16}" y="${p.y+26}">${esc(dd.name)}</text><text class="dsub" x="${p.x+16}" y="${p.y+44}">${esc(truncate(dd.subtitle, Math.floor(p.w/7.2)))}</text>`;
    const items = (byD[d]||[]).slice();
    const lots = DATA.lots_per_district[d]||0;
    const n = items.length + lots;
    const inner = p.w - 32; const step = Math.min(BW+GAP, inner / Math.max(n,1)); const bw = Math.min(BW, step-8);
    const base = p.y + p.h - 56; let x = p.x + 16 + (inner - step*n)/2 + (step-bw)/2;
    items.forEach((b,i) => { const ly = (n > 1 && i%2) ? 34 : 18; b._x = x + bw/2; b._y = base; const h = HEIGHTS[b.shape]||90; const shp = (SHAPES[b.shape]||SHAPES.small)(bw,h);
      s += `<g class="bld" data-id="${b.id}" data-aud="${b.audience}" transform="translate(${x},${base})"><rect class="glow" x="-4" y="${-h-6}" width="${bw+8}" height="${h+8}" rx="6"/><g class="body">${shp}</g><text x="${bw/2}" y="${ly}">${esc(b.name)}</text></g>`;
      x += step; });
    for (let i=0;i<lots;i++){ s += `<g class="lot" transform="translate(${x},${base})">${SHAPES.lot(bw,30)}<text x="${bw/2}" y="${(n > 1 && (items.length+i)%2) ? 34 : 18}" style="font-size:11px;fill:#6b7d6b;text-anchor:middle">free lot</text></g>`; x += step; }
    s += `</g>`;
  });
  s += `<polyline id="path" points=""/><g id="badges"></g>`;
  svg.innerHTML = s;
  svg.querySelectorAll('.bld').forEach(g => {
    g.addEventListener('click', () => openB(g.dataset.id));
    g.addEventListener('mousemove', e => tip(e, g.dataset.id));
    g.addEventListener('mouseleave', () => $('#tip').style.display='none');
  });
  applyFilter(); applySelection();
}
function truncate(s,n){ return s.length>n ? s.slice(0,n-1)+'…' : s; }

/* ---------- tooltip */
function tip(e, id){
  const b = DATA.buildings.find(x=>x.id===id); const t = $('#tip'); const wrap = $('#cityWrap').getBoundingClientRect();
  const d = DATA.districts.find(x=>x.id===b.district)||{};
  t.innerHTML = `<b>${esc(b.name)}</b>${b.sub?`<div style="color:${d.color||'#555'};font-weight:600;margin-bottom:3px">${esc(b.sub)}</div>`:''}${esc(b.pitch)}${b.mode&&DATA.modes[b.mode]?`<div style="margin-top:4px;color:#5b6773;font-size:12px">${esc(DATA.modes[b.mode])} · ${esc(d.name||'')}</div>`:''}`; t.style.display='block';
  let x = e.clientX - wrap.left + 14, y = e.clientY - wrap.top + 14; if (x + 290 > wrap.width) x -= 300; t.style.left = x+'px'; t.style.top = y+'px';
}

/* ---------- filter & wayfinder */
let aud = 'all';
const areaColor = id => (DATA.districts.find(d=>d.id===id)||{}).color || '#e6c76b';
const fits = a => aud==='all' || a===aud || a==='everyone';
function applyFilter(){
  document.querySelectorAll('.bld').forEach(g => g.classList.toggle('dim', !fits(g.dataset.aud)));
  document.querySelectorAll('#who .chip').forEach(c=>c.classList.toggle('on', c.dataset.a===aud));
  document.querySelectorAll('#way .chip[data-journey]').forEach(c => { const j = DATA.journeys.find(x=>x.id===c.dataset.journey); c.hidden = !fits(j.audience||'everyone'); });
  document.querySelectorAll('#aud .chip[data-district]').forEach(c => { const d = DATA.districts.find(x=>x.id===c.dataset.district); c.hidden = !fits(d.audience||'everyone'); });
}
(function(){
  const who = $('#who'); const mk=(a,l)=>{const b=document.createElement('button'); b.className='chip'; b.dataset.a=a; b.textContent=l; b.onclick=()=>{aud=a; applyFilter(); try{localStorage.setItem('city.aud',a);}catch(e){}}; who.appendChild(b);};
  mk('all','Show me everything'); Object.entries(DATA.audiences).forEach(([a,l])=>{ if(a!=='everyone') mk(a,l); });
  try { const saved = localStorage.getItem('city.aud'); if (saved && (saved==='all' || DATA.audiences[saved])) aud = saved; } catch(e) {}
  const bar = $('#aud');
  DATA.districts.forEach(d => { if (d.auto && !DATA.buildings.some(b=>b.district===d.id)) return; const c=document.createElement('button'); c.className='chip'; c.dataset.district=d.id; c.innerHTML=`<span class="dot" style="background:${d.color}"></span>${esc(d.name)}`; c.title=d.subtitle; c.onclick=()=>select({type:'district', id:d.id}); bar.appendChild(c); });
  if (DATA.scene) {
    const t0=document.createElement('button'); t0.className='chip'; t0.textContent='Colour areas'; t0.onclick=()=>{t0.classList.toggle('on'); $('#city').classList.toggle('areas');}; bar.appendChild(t0);
    const t1=document.createElement('button'); t1.className='chip'; t1.textContent='All names'; t1.onclick=()=>{t1.classList.toggle('on'); $('#city').classList.toggle('alllabels');}; bar.appendChild(t1);
    const t2=document.createElement('button'); t2.className='chip'; t2.textContent=`Free lots (${DATA.free_lots.length})`; t2.onclick=()=>{showLots=!showLots; t2.classList.toggle('on',showLots); $('#city').classList.toggle('lots',showLots);}; bar.appendChild(t2); }
  const way = $('#way'); DATA.journeys.forEach(j => { const b=document.createElement('button'); b.className='chip'; b.dataset.journey=j.id; b.innerHTML=`<span class="dot" style="background:${areaColor(j.area)}"></span>${esc(j.q)}`; b.title=j.when; b.onclick=()=>select({type:'journey', id:j.id}); way.appendChild(b); });
  const fd = DATA.buildings.find(b=>b.picker); if (fd) { const b=document.createElement('button'); b.className='chip tour'; b.textContent='Not sure? Ask the Front Desk'; b.onclick=()=>openB(fd.id); way.appendChild(b); }
})();

/* ---------- persistent selection: a journey (numbered stops + path + panel) or a district */
let sel = null, stop = 0;
function select(next){
  if (sel && next && sel.type===next.type && sel.id===next.id) next = null;   // click again = unselect
  sel = next; stop = 0; closeB(); applySelection();
  if (sel) { const first = sel.type==='journey' ? DATA.journeys.find(j=>j.id===sel.id).stops[0].building : (DATA.buildings.find(b=>b.district===sel.id)||{}).id; const g = first && document.querySelector(`.bld[data-id="${first}"]`); g && g.scrollIntoView({behavior:'smooth',block:'center'}); }
}
function applySelection(){
  document.querySelectorAll('.chip[data-journey],.chip[data-district]').forEach(c => c.classList.toggle('sel', !!sel && ((sel.type==='journey' && c.dataset.journey===sel.id) || (sel.type==='district' && c.dataset.district===sel.id))));
  const path = $('#path'), badges = $('#badges'); if (path) path.setAttribute('points',''); if (badges) badges.innerHTML='';
  document.querySelectorAll('.bld').forEach(g => { g.classList.remove('focus','cur'); });
  document.querySelectorAll('.lm').forEach(g => g.classList.toggle('on', !!sel && sel.type==='journey' && g.dataset.journey===sel.id));
  const guide = $('#guide'); $('#city').classList.toggle('picked', !!sel);
  if (!sel) { guide.style.display='none'; return; }
  guide.querySelector('.facts').innerHTML = '';
  if (sel.type==='district') {
    const d = DATA.districts.find(x=>x.id===sel.id); guide.style.setProperty('--gac', d.color);
    { const xs = DATA.buildings.filter(b=>b.district===sel.id && b._x!==undefined).map(b=>b._x); const W0 = DATA.scene ? DATA.scene.w : 1440; guide.classList.toggle('left', xs.length>0 && xs.reduce((p,q)=>p+q,0)/xs.length > W0*0.55); }
    document.querySelectorAll('.bld').forEach(g => { const b=DATA.buildings.find(x=>x.id===g.dataset.id); g.classList.toggle('focus', b.district===sel.id); });
    guide.querySelector('.who').textContent = d.name; guide.querySelector('.when').textContent = d.subtitle;
    const js = DATA.journeys.filter(j=>j.area===sel.id);
    guide.querySelector('.facts').innerHTML = js.length ? `<b>Routes</b><span>${js.map(j=>`<a href="#${j.id}" data-j="${j.id}">${esc(j.q)}</a>`).join(' · ')}</span>` : '';
    guide.querySelectorAll('.facts a').forEach(a => a.onclick = e => { e.preventDefault(); select({type:'journey', id:a.dataset.j}); });
    guide.querySelector('.stops').innerHTML = DATA.buildings.filter(b=>b.district===sel.id).map(b=>`<li data-b="${b.id}"><b>${esc(b.name)}</b>${esc(b.sub||b.pitch)}</li>`).join('');
    guide.querySelector('.nav').style.display='none';
  } else {
    const j = DATA.journeys.find(x=>x.id===sel.id); const k = DATA.scene ? DATA.scene.w/1440 : 1;
    guide.style.setProperty('--gac', areaColor(j.area));
    guide.querySelector('.facts').innerHTML = [['You bring', j.bring], ['You get', j.get], ['Takes', j.time]].filter(r=>r[1]).map(r=>`<b>${r[0]}</b><span>${esc(r[1])}</span>`).join('');
    const pts = [];
    j.stops.forEach((st,i) => { const b = DATA.buildings.find(x=>x.id===st.building); const g = document.querySelector(`.bld[data-id="${st.building}"]`); if (!g || b._x===undefined) return; g.classList.add('focus'); if (i===stop) g.classList.add('cur');
      const y = b._y - 12*k; pts.push(`${b._x},${y}`);
      badges.innerHTML += `<g class="badge" transform="translate(${b._x},${y})"><circle r="${12*k}" style="fill:${areaColor(j.area)}"/><text y="${4.5*k}" style="font-size:${13*k}px">${i+1}</text></g>`; });
    path.setAttribute('points', pts.join(' ')); path.style.stroke = areaColor(j.area);
    const xs = j.stops.map(st => (DATA.buildings.find(x=>x.id===st.building)||{})._x).filter(x=>x!==undefined); const W0 = DATA.scene ? DATA.scene.w : 1440;
    guide.classList.toggle('left', xs.length && xs.reduce((a,b)=>a+b,0)/xs.length > W0*0.55);
    guide.querySelector('.who').textContent = j.q; guide.querySelector('.when').innerHTML = `<b>When:</b> ${esc(j.when)}`;
    guide.querySelector('.stops').innerHTML = j.stops.map((st,i)=>{ const b=DATA.buildings.find(x=>x.id===st.building); return `<li class="${i===stop?'cur':''}" data-i="${i}" data-b="${st.building}"><b>${esc(b.name)}</b>${esc(st.say)}</li>`; }).join('');
    guide.querySelector('.nav').style.display=''; $('#gPrev').disabled = stop===0; $('#gNext').disabled = stop===j.stops.length-1;
  }
  guide.style.display='block';
  guide.querySelectorAll('li').forEach(li => li.onclick = () => { if (li.dataset.i!==undefined) { stop = +li.dataset.i; applySelection(); } openB(li.dataset.b); });
}
$('#gClose').onclick = () => select(null);
$('#gPrev').onclick = () => { if (stop>0) { stop--; applySelection(); } };
$('#gNext').onclick = () => { const j = DATA.journeys.find(x=>x.id===sel.id); if (stop < j.stops.length-1) { stop++; applySelection(); } };
$('#gOpen').onclick = () => { const j = DATA.journeys.find(x=>x.id===sel.id); openB(j.stops[stop].building); };

/* ---------- modal */
function codeBlock(text){ return `<div class="code"><button class="copy" type="button">Copy</button><pre>${esc(text)}</pre></div>`; }
function openB(id){
  const b = DATA.buildings.find(x=>x.id===id); if(!b) return;
  const d = DATA.districts.find(x=>x.id===b.district);
  const cj = sel && sel.type==='journey' ? DATA.journeys.find(j=>j.id===sel.id) : null;
  let h = `<div class="areabar" style="background:${d.color}"></div><h2>${esc(b.name)}</h2>${b.sub?`<div class="sub">${esc(b.sub)}</div>`:''}<div class="meta"><span><span class="dot" style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${d.color};margin-right:5px"></span>${esc(d.name)}</span><span class="aud">${esc(DATA.audiences[b.audience]||b.audience)}</span>${b.mode&&DATA.modes[b.mode]?`<span class="mode ${esc(b.mode)}">${esc(DATA.modes[b.mode])}</span>`:''}${b.auto?'<span class="aud" style="background:#fff3c4">not yet placed on the map — add it to city/city.json</span>':''}</div>`;
  h += `<p class="pitch">${esc(b.pitch)}</p>`;
  if (cj) { const i = cj.stops.findIndex(s=>s.building===b.id); if (i>=0) h += `<p class="say" style="background:#fff7d6;border-radius:8px;padding:6px 10px;font-size:14px"><b>Step ${i+1} of ${cj.stops.length} — ${esc(cj.q)}:</b> ${esc(cj.stops[i].say)}</p>`; }
  if (b.picker) {
    const groups = [['everyone','Anyone'], ...Object.entries(DATA.audiences).filter(([a])=>a!=='everyone')];
    groups.forEach(([a,label]) => { const js = DATA.journeys.filter(j => (j.audience||'everyone')===a && fits(j.audience||'everyone')); if (!js.length) return;
      h += `<div class="grp">${esc(a==='everyone'?'Anyone':'If you work in '+label)}</div><div class="cards">` + js.map(j => `<div class="card" style="--ac:${areaColor(j.area)}"><h4>${esc(j.q)}</h4><div class="v">${esc(j.when)}</div><div class="k">You bring</div><div class="v">${esc(j.bring||'')}</div><div class="k">You get</div><div class="v">${esc(j.get||'')}</div><div class="k">Takes</div><div class="v">${esc(j.time||'')}</div><button class="chip" data-go="${j.id}">Show me the route ›</button></div>`).join('') + `</div>`; });
  }
  if (b.asks && b.asks.length){
    h += `<h3>${b.mode==='auto'?'What you get':'Ask it'}</h3><table class="asks"><thead><tr><th>${b.mode==='auto'?'You do':'Say'}</th><th>When</th><th>You get</th></tr></thead><tbody>`;
    b.asks.forEach(a => { const cls = cj && a.journeys ? (a.journeys.includes(cj.id) ? 'hi' : 'lo') : ''; const auto = a.say.startsWith('(');
      h += `<tr class="${cls}"><td class="say">${auto?`<i>${esc(a.say.slice(1,-1))}</i>`:codeBlock(a.say)}</td><td>${esc(a.when)}</td><td>${esc(a.get)}</td></tr>`; });
    h += `</tbody></table>`;
  }
  if (b.steps.length){ h += `<h3>How to use it</h3>`; b.steps.forEach(s => { h += `<div class="step">${s.say?`<p class="say">${s.say}</p>`:''}${s.copy?codeBlock(s.copy):''}</div>`; }); }
  if (b.prompts.length){ h += `<h3>The prompts behind it</h3>`; b.prompts.forEach(p => { h += `<details><summary><code>/${esc(p.name)}</code></summary><div class="desc">${esc(p.description)}</div><div class="desc">What it tells Copilot (you do not paste this; it runs when you type the command in a workspace that has <code>${esc(p.file)}</code>):</div>${codeBlock(p.body)}</details>`; }); }
  if (b.agents.length){ h += `<h3>Agents</h3>`; b.agents.forEach(a => { h += `<details><summary><code>@${esc(a.name)}</code></summary><div class="desc">${esc(a.description)}</div>${codeBlock(a.body)}</details>`; }); }
  if (b.docs.length){ h += `<h3>${b.docs.length>1?'Full instructions':'Full instructions'}</h3>`; b.docs.forEach((doc,i) => { h += `<details ${b.steps.length?'':'open'}><summary>${esc(doc.title)}</summary><div class="doc">${doc.html}</div></details>`; }); }
  if (b.source) h += `<div class="src">Source: <code>${esc(b.source)}</code></div>`;
  $('#mc').innerHTML = h; $('#ov').classList.add('on'); $('#ov').scrollTop = 0;
  $('#mc').querySelectorAll('.copy').forEach(btn => btn.onclick = () => copy(btn));
  $('#mc').querySelectorAll('[data-go]').forEach(btn => btn.onclick = () => select({type:'journey', id:btn.dataset.go}));
}
function closeB(){ $('#ov').classList.remove('on'); }
$('#mx').onclick = closeB; $('#ov').addEventListener('click', e => { if (e.target.id==='ov') closeB(); });
document.addEventListener('keydown', e => { if (e.key==='Escape') closeB(); });
function copy(btn){ const text = btn.parentElement.querySelector('pre').textContent; const done=()=>{btn.textContent='Copied'; btn.classList.add('done'); setTimeout(()=>{btn.textContent='Copy'; btn.classList.remove('done');},1400);};
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, ()=>fallback(text,done)); else fallback(text,done); }
function fallback(text,done){ const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); done(); }catch(e){} document.body.removeChild(ta); }

render();
applyFilter();
if (location.hash) { const id = decodeURIComponent(location.hash.slice(1)); if (DATA.buildings.some(b=>b.id===id)) openB(id); else if (DATA.journeys.some(j=>j.id===id)) select({type:'journey', id}); else if (DATA.districts.some(d=>d.id===id)) select({type:'district', id}); }
</script>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if the repo has features not placed on the map")
    ap.add_argument("--out", help="output path (default: manifest 'output', i.e. index.html at the repo root)")
    ap.add_argument("--link-image", action="store_true", help="reference city/scene.* instead of embedding it (smaller file, two files to share)")
    a = ap.parse_args()
    m = load_manifest()
    ids = [b["id"] for b in m["buildings"]]
    if len(ids) != len(set(ids)):
        die("duplicate building ids in city.json")
    dids = {d["id"] for d in m["districts"]}
    for b in m["buildings"]:
        if b["district"] not in dids:
            die(f"building {b['id']} points at unknown district {b['district']}")
    jids = {j["id"] for j in m["journeys"]}
    for j in m["journeys"]:
        if j.get("area") and j["area"] not in dids:
            die(f"journey {j['id']} points at unknown area {j['area']}")
        for st in j["stops"]:
            if st["building"] not in ids:
                die(f"journey {j['id']} points at unknown building {st['building']}")
    for lm in m.get("landmarks", []):
        if lm["journey"] not in jids:
            die(f"landmark '{lm['name']}' points at unknown journey {lm['journey']}")
    for b in m["buildings"]:
        for row in b.get("asks", []):
            for jid in row.get("journeys", []):
                if jid not in jids:
                    die(f"building {b['id']}: an 'asks' row points at unknown journey {jid}")
    data, unmapped = build_data(m, a.link_image)
    page = (PAGE.replace("__TITLE__", html.escape(m["title"])).replace("__TAGLINE__", html.escape(m["tagline"]))
            .replace("__BUILT__", data["built"])
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    for k in m["redact"]:
        if k in page:
            die(f"redaction failed: '{k}' still present in output")
    out = Path(a.out) if a.out else ROOT / m.get("output", "index.html")
    out.write_text(page, encoding="utf-8")
    rel_out = out.relative_to(ROOT) if str(out).startswith(str(ROOT)) else out
    if data["scene"]:
        sc = data["scene"]
        placed = sum(1 for b in data["buildings"] if b.get("hotspot"))
        print(f"{rel_out}: illustrated mode — {sc['file']} {sc['w']}x{sc['h']} ({sc['bytes']//1024} KB), "
              f"{len(sc['hotspots'])} hotspots: {placed} buildings, {len(data['free_lots'])} free lots; page {len(page)//1024} KB")
        auto = [b for b in data["buildings"] if b.get("hotspot_auto")]
        if auto:
            print("placed on free lots automatically (give them a 'hotspot' in city.json to pin them): "
                  + ", ".join(f"{b['id']}→{b['hotspot']}" for b in auto))
    else:
        print(f"{rel_out}: drawn mode (no city/scene.png|jpg) — {len(data['buildings'])} buildings, "
              f"{len(m['districts'])} districts, {len(page)//1024} KB")
    if unmapped:
        print(f"{len(unmapped)} feature(s) not placed on the map — shown in New Arrivals until you add them to city/city.json:")
        for kind, key, rel, desc in unmapped:
            print(f"  [{kind}] {key}  ({rel})  {desc[:70]}")
        if a.check:
            sys.exit(1)
    else:
        print("every prompt, agent and build sheet in the repo has a building")


if __name__ == "__main__":
    main()
