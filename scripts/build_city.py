"""Build index.html — the walkable 2D city of everything SemiAgency offers — from city/city.json and the repo.

    python scripts/build_city.py            # writes index.html, reports unmapped features
    python scripts/build_city.py --check    # exit 1 if any feature in the repo is not placed on the map

The page is self-contained (no network, no corporate data): it embeds the painting city/scene.jpg, the
traced city/hotspots.json, the page template city/template.html, the prompt files, the M365 build sheets and
the docs the manifest names, after applying the manifest's `redact` map. Anything new in .github/prompts,
.github/agents, m365/ or agents/ that no building claims is placed automatically in the "New Arrivals"
district (on a free lot) so the map never silently lags the repo. Python 3 standard library only.
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
TEMPLATE = ROOT / "city" / "template.html"
HOTSPOTS = ROOT / "city" / "hotspots.json"


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
                    if lines[i].strip() and stack and lines[i].startswith(" " * (stack[-1][0] + 2)):
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


def copy_from(ref, m):
    """'m365/01-daily-brief.md#block1' -> the first ``` block of that file; '#instructions' -> the text between
    === INSTRUCTIONS === and === END ===. Lets a step copy the exact prompt from its build sheet (one source)."""
    rel, _, sel = ref.partition("#")
    text = read(rel, m)
    if sel == "instructions":
        mt = re.search(r"^=== INSTRUCTIONS ===\n(.*?)\n=== END ===", text, re.S | re.M)
        if not mt:
            die(f"copy_from {ref}: no === INSTRUCTIONS === ... === END === block")
        return mt.group(1).strip()
    mt = re.fullmatch(r"block(\d+)", sel or "block1")
    if not mt:
        die(f"copy_from {ref}: use #blockN or #instructions")
    blocks = re.findall(r"^```[^\n]*\n(.*?)^```", text, re.S | re.M)
    n = int(mt.group(1))
    if n > len(blocks):
        die(f"copy_from {ref}: the file has only {len(blocks)} code blocks")
    return blocks[n - 1].strip()


def prompt_info(name, m):
    rel = f".github/prompts/{name}.prompt.md"
    raw = read(rel, m)
    meta, body = strip_frontmatter(raw)
    return {"name": name, "file": rel, "description": meta.get("description", ""),
            "body": body.strip(), "raw": raw}


def agent_info(name, m):
    rel = f".github/agents/{name}.agent.md"
    raw = read(rel, m)
    meta, body = strip_frontmatter(raw)
    return {"name": name, "file": rel, "description": meta.get("description", ""), "body": body.strip(), "raw": raw}


def doc_info(d, m):
    text = read(d["file"], m)
    _, body = strip_frontmatter(text)
    return {"title": d.get("title", d["file"]), "file": d["file"], "html": md_to_html(body), "raw": text}


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


# ---------------------------------------------------------------- scene (the painting) and hotspots

def image_size(data):
    """(width, height) of a PNG or JPEG from its bytes; stdlib only."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
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


def load_scene():
    """city/scene.png|jpg + city/hotspots.json → dict for the page. Both are required."""
    cdir = ROOT / "city"
    img = next((p for ext in ("png", "jpg", "jpeg") for p in [cdir / f"scene.{ext}"] if p.is_file()), None)
    if not img:
        die("missing city/scene.jpg (or .png) — the painting the city is drawn on; see city/README.md")
    if not HOTSPOTS.is_file():
        die("missing city/hotspots.json — trace the buildings on the painting with city/hotspot-editor.html")
    data = img.read_bytes()
    w, h = image_size(data)
    spots = json.loads(HOTSPOTS.read_text(encoding="utf-8"))["hotspots"]
    ids = [x["id"] for x in spots]
    if len(ids) != len(set(ids)):
        die("duplicate hotspot ids in city/hotspots.json")
    for x in spots:
        if len(x.get("points", [])) < 3:
            die(f"hotspot {x['id']} has fewer than 3 points")
    mime = "image/png" if img.suffix == ".png" else "image/jpeg"
    return {"src": f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}", "w": w, "h": h,
            "hotspots": spots, "file": img.name, "bytes": len(data)}


def assign_hotspots(buildings, scene, landmarks=()):
    """Buildings and landmarks name their hotspot in city.json; buildings without one take the free lots
    (hotspots nobody claims) in order. Returns the hotspot ids still free."""
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
                print(f"warning: no free lot left for {b['id']}; it is only reachable from the panel")
                continue
            b["hotspot"] = free.pop(0)
            b["hotspot_auto"] = True
    return free


# ---------------------------------------------------------------- assembling

def build_data(m):
    claimed = claimed_keys(m)
    unmapped = [f for f in scan_features() if (f[0], f[1]) not in claimed]
    buildings = []
    for b in m["buildings"]:
        d = dict(b)
        d["prompts"] = [prompt_info(p, m) for p in b.get("prompts", [])]
        d["agents"] = [agent_info(a, m) for a in b.get("agents", [])]
        d["docs"] = [doc_info(x, m) for x in b.get("docs", [])]
        d["steps"] = [{"say": inline(s.get("say", "")),
                       "copy": s.get("copy") or (copy_from(s["copy_from"], m) if s.get("copy_from") else ""),
                       "long": bool(s.get("copy_from")), "setup": bool(s.get("setup"))} for s in b.get("steps", [])]
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
    data = {k: m[k] for k in ("title", "tagline", "audiences", "districts", "journeys")}
    data["modes"] = m.get("modes", {})
    data["landmarks"] = [dict(lm) for lm in m.get("landmarks", [])]
    scene = load_scene()
    data["free_lots"] = assign_hotspots(buildings, scene, data["landmarks"])
    data["scene"] = scene
    data["area_label_at"] = m.get("area_label_at", {})
    for d in buildings:
        d["asks"] = [dict(a, when=a.get("when", ""), get=a.get("get", "")) for a in d.get("asks", [])]
    data["buildings"] = buildings
    data["built"] = date.today().isoformat()
    data["version"] = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").is_file() else ""
    return data, unmapped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if the repo has features not placed on the map")
    ap.add_argument("--out", help="output path (default: manifest 'output', i.e. index.html at the repo root)")
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
    if not TEMPLATE.is_file():
        die(f"missing {TEMPLATE.relative_to(ROOT)}")
    data, unmapped = build_data(m)
    page = TEMPLATE.read_text(encoding="utf-8")
    for k, v in (("__TITLE__", html.escape(m["title"])), ("__TAGLINE__", html.escape(m["tagline"])),
                 ("__BUILT__", data["built"]), ("__VERSION__", html.escape(data["version"]))):
        page = page.replace(k, v)
    page = page.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"), 1)
    for k in m["redact"]:
        if k in page:
            die(f"redaction failed: '{k}' still present in output")
    out = Path(a.out) if a.out else ROOT / m.get("output", "index.html")
    out.write_text(page, encoding="utf-8")
    rel_out = out.relative_to(ROOT) if str(out).startswith(str(ROOT)) else out
    auto = [b for b in data["buildings"] if b.get("hotspot_auto")]
    sc = data["scene"]
    print(f"{rel_out}: {sc['file']} {sc['w']}x{sc['h']} ({sc['bytes']//1024} KB), {len(data['buildings'])} buildings, "
          f"{len(m['districts'])} districts, {len(data['journeys'])} routes, {len(data['free_lots'])} free lots; page {len(page)//1024} KB")
    if auto:
        print("placed on free lots automatically (give them a 'hotspot' in city.json to pin them): "
              + ", ".join(f"{b['id']}→{b['hotspot']}" for b in auto))
    if data["free_lots"]:
        print("free lots (hotspot ids you can give to a new building): " + ", ".join(data["free_lots"]))
    if unmapped:
        print(f"{len(unmapped)} feature(s) not placed on the map — shown in New Arrivals until you add them to city/city.json "
              f"(or run scripts/new_prompt.py next time):")
        for kind, key, rel, desc in unmapped:
            print(f"  [{kind}] {key}  ({rel})  {desc[:70]}")
        if a.check:
            sys.exit(1)
    else:
        print("every prompt, agent and build sheet in the repo has a building")


if __name__ == "__main__":
    main()
