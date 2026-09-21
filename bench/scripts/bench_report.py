"""Build index.html (models × cases pass-rate matrix + side-by-side outputs) from runs/ and results/.

    python scripts/bench_report.py            # writes index.html, prints a summary line
    python scripts/bench_report.py --pending  # lists runs without a result (used by /bench-judge)
"""
import argparse
import html
import json
from collections import defaultdict
from datetime import datetime

import benchlib as B


def collect():
    rows = []
    for run in B.list_runs():
        meta, body = B.parse_header(run.read_text(encoding="utf-8"))
        res = B.load_result(run)
        rows.append({
            "case": run.parent.name, "stem": run.stem,
            "model": meta.get("model", run.stem.split("__")[0]),
            "date": meta.get("date", ""), "mode": meta.get("mode", "?"),
            "error": meta.get("error"), "output": body.strip(),
            "result": res,
        })
    return rows


def summarize(rows):
    """{(model, case): {"n": runs, "graded": k, "passed": p, "total": t}}"""
    agg = defaultdict(lambda: {"n": 0, "graded": 0, "passed": 0, "total": 0})
    judges = set()
    for r in rows:
        a = agg[(r["model"], r["case"])]
        a["n"] += 1
        if r["result"]:
            a["graded"] += 1
            a["passed"] += r["result"].get("passed", 0)
            a["total"] += r["result"].get("total", 0)
            judges.add(r["result"].get("judge_model", "?"))
    return agg, judges


def cell_class(a):
    if a["total"] == 0:
        return "na"
    p = a["passed"] / a["total"]
    return "good" if p >= 0.999 else "ok" if p >= 0.6 else "bad"


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>bench</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#ddd;--good:#d7f5dc;--ok:#fff3c4;--bad:#ffd9d9;--na:#f2f2f2;--card:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--mut:#aaa;--line:#333;--good:#1e4d2b;--ok:#5a4a12;--bad:#5c1f1f;--na:#242424;--card:#1e1e1e}}
body{font:15px/1.45 system-ui,sans-serif;margin:0;padding:16px;background:var(--bg);color:var(--fg)}
h1{font-size:20px;margin:0 0 4px}.mut{color:var(--mut)}
table{border-collapse:collapse;margin:16px 0}th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
td.c{cursor:pointer;text-align:center;font-variant-numeric:tabular-nums}
td.good{background:var(--good)}td.ok{background:var(--ok)}td.bad{background:var(--bad)}td.na{background:var(--na);color:var(--mut)}
tr.sel td.c.on{outline:2px solid var(--fg);outline-offset:-2px}
#side{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.card{border:1px solid var(--line);border-radius:6px;background:var(--card);padding:10px;overflow:auto;max-height:70vh}
.card h3{margin:0 0 6px;font-size:14px}.card pre{white-space:pre-wrap;font:13px/1.4 ui-monospace,monospace;margin:8px 0}
.chk{font-size:13px;margin:2px 0}.PASS::before{content:"✓ ";color:#2a8a3a}.FAIL::before{content:"✗ ";color:#c33}
.ev{color:var(--mut);margin-left:18px;font-style:italic}
select,button{font:inherit;padding:4px 8px}
</style></head><body>
<h1>Personal model benchmark</h1>
<div class="mut">__SUBTITLE__</div>
<table id="m"><thead><tr><th>case \\ model</th>__MODELHEAD__</tr></thead><tbody>__ROWS__</tbody></table>
<div class="mut">Cell = checks passed / checks total over all graded runs (runs in brackets). Click a case name for its outputs side by side; click a cell to jump to that model.</div>
<h2 id="ct" style="font-size:16px"></h2>
<div id="side"></div>
<script>
const DATA=__DATA__;
const CHECKS=__CHECKS__;
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function show(cs,focus){
  document.querySelectorAll('tr.sel').forEach(t=>t.classList.remove('sel'));
  const tr=document.querySelector('tr[data-case="'+cs+'"]');if(tr)tr.classList.add('sel');
  document.getElementById('ct').textContent=cs;
  const runs=DATA.filter(r=>r.case===cs).sort((a,b)=>a.model.localeCompare(b.model)||a.date.localeCompare(b.date));
  const side=document.getElementById('side');side.innerHTML='';
  const byModel={};runs.forEach(r=>(byModel[r.model]=byModel[r.model]||[]).push(r));
  for(const m of Object.keys(byModel).sort()){
    const card=document.createElement('div');card.className='card';if(m===focus)card.style.outline='2px solid var(--fg)';
    let h='<h3>'+esc(m)+' <span class="mut">('+byModel[m].length+' run'+(byModel[m].length>1?'s':'')+')</span></h3>';
    const sel=byModel[m].length>1?'<select onchange="pick(this)">'+byModel[m].map((r,i)=>'<option value="'+i+'">'+esc(r.stem)+(r.result?' — '+r.result.passed+'/'+r.result.total:' — ungraded')+'</option>').join('')+'</select>':'';
    card.innerHTML=h+sel+'<div class="body"></div>';card.dataset.model=m;card.dataset.case=cs;side.appendChild(card);
    render(card,byModel[m][0]);
  }
}
function pick(sel){const card=sel.closest('.card');const runs=DATA.filter(r=>r.case===card.dataset.case&&r.model===card.dataset.model).sort((a,b)=>a.date.localeCompare(b.date));render(card,runs[sel.value]);}
function render(card,r){
  let h='';
  if(r.error)h+='<div class="FAIL chk">'+esc(r.error)+'</div>';
  if(r.result){h+='<div class="mut">'+r.result.passed+'/'+r.result.total+' · judge '+esc(r.result.judge_model)+'</div>';
    r.result.checks.forEach(c=>{h+='<div class="chk '+c.verdict+'">'+esc(c.id)+' '+esc(c.check||'')+'</div><div class="ev">'+esc(c.evidence)+'</div>';});}
  else h+='<div class="mut">ungraded'+(CHECKS[r.case]?'':' — no checks.md yet')+'</div>';
  h+='<pre>'+esc(r.output||'(empty output)')+'</pre>';
  card.querySelector('.body').innerHTML=h;
}
document.querySelectorAll('td.c').forEach(td=>td.onclick=()=>show(td.dataset.case,td.dataset.model));
document.querySelectorAll('th.case').forEach(th=>th.onclick=()=>show(th.dataset.case));
if(location.hash)show(decodeURIComponent(location.hash.slice(1)));else if(DATA.length)show(DATA[0].case);
</script></body></html>
"""


def build_html(rows):
    agg, judges = summarize(rows)
    models = sorted({r["model"] for r in rows})
    cases = sorted({r["case"] for r in rows})
    head = "".join(f"<th>{html.escape(m)}</th>" for m in models)
    body = []
    for c in cases:
        tds = []
        for m in models:
            a = agg.get((m, c))
            if not a:
                tds.append(f'<td class="c na" data-case="{html.escape(c)}" data-model="{html.escape(m)}">–</td>')
                continue
            txt = f'{a["passed"]}/{a["total"]}' if a["total"] else "ungraded"
            tds.append(f'<td class="c {cell_class(a)}" data-case="{html.escape(c)}" data-model="{html.escape(m)}">'
                       f'{txt} <span class="mut">[{a["n"]}]</span></td>')
        body.append(f'<tr data-case="{html.escape(c)}"><th class="case" data-case="{html.escape(c)}" style="cursor:pointer">{html.escape(c)}</th>{"".join(tds)}</tr>')
    graded = sum(1 for r in rows if r["result"])
    sub = (f"{len(rows)} runs, {graded} graded · {len(cases)} cases · {len(models)} models · "
           f"judge: {', '.join(sorted(judges)) or 'none yet'} · built {datetime.now():%Y-%m-%d %H:%M}")
    if len(judges) > 1:
        sub += " · <b>warning: more than one judge model — results are not comparable</b>"
    checks = {c: bool(B.read_checks(c)) for c in cases}
    slim = [{k: v for k, v in r.items()} for r in rows]
    return (PAGE.replace("__SUBTITLE__", sub).replace("__MODELHEAD__", head).replace("__ROWS__", "".join(body))
            .replace("__DATA__", json.dumps(slim, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__CHECKS__", json.dumps(checks)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending", action="store_true", help="list runs without results and cases without checks")
    ap.add_argument("--case", help="filter for --pending")
    a = ap.parse_args()
    if a.pending:
        cases = [a.case] if a.case else B.list_cases()
        no_checks = [c for c in cases if not B.read_checks(c) and B.list_runs(c)]
        for c in no_checks:
            print(f"no checks: {c}  (run /bench-feedback case={c} first)")
        pend = [p for p in B.pending_runs(a.case) if p.parent.name not in no_checks]
        for p in pend:
            print(p.relative_to(B.ROOT).as_posix())
        print(f"{len(pend)} pending")
        return
    rows = collect()
    if not rows:
        B.die("no runs yet under runs/")
    out = B.ROOT / "index.html"
    out.write_text(build_html(rows), encoding="utf-8")
    agg, judges = summarize(rows)
    per_model = defaultdict(lambda: [0, 0])
    for (m, _), a in agg.items():
        per_model[m][0] += a["passed"]
        per_model[m][1] += a["total"]
    line = "  ".join(f"{m} {p}/{t}" for m, (p, t) in sorted(per_model.items()) if t)
    print(f"index.html: {len(rows)} runs, {sum(1 for r in rows if r['result'])} graded; {line or 'nothing graded yet'}")
    if len(judges) > 1:
        print(f"warning: {len(judges)} different judge models used — results are not comparable")


if __name__ == "__main__":
    main()
