import json, csv
from pathlib import Path
from collections import Counter

def export_all(findings, outdir="reports"):
    out=Path(outdir); out.mkdir(exist_ok=True)
    export_json(findings,out)
    export_csv(findings,out)
    export_txt(findings,out)
    export_html(findings,out)

def export_json(findings,out):
    (out/"linuxcmdscan_results.json").write_text(
        json.dumps([f.__dict__ for f in findings],indent=2)
    )

def export_csv(findings,out):
    if not findings: return
    with open(out/"linuxcmdscan_results.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=findings[0].__dict__.keys())
        w.writeheader()
        for r in findings: w.writerow(r.__dict__)

def export_txt(findings,out):
    with open(out/"linuxcmdscan_results.txt","w",encoding="utf-8") as f:
        for i,r in enumerate(findings,1):
            f.write(f"[{i}] {r.file}:{r.line} {r.command}\n")

def export_html(findings,out):
    counts=Counter(f.severity for f in findings)
    def card(sev):
        return f"<div class='card {sev}'><div>{sev.upper()}</div><div>{counts.get(sev,0)}</div></div>"
    rows="".join(
        f"<tr><td>{r.file}</td><td>{r.line}</td><td>{r.detected_command}</td>"
        f"<td>{r.severity}</td><td><code>{r.command}</code></td></tr>"
        for r in findings
    )
    (out/"linuxcmdscan_report.html").write_text(f"""<!doctype html>
<html>
<head>
<meta charset=utf-8>
<title>linuxcmdscan Report</title>
<style>
:root {{
--bg:#fff; --fg:#000; --card:#f4f4f4; --table:#ddd;
}}
[data-theme=dark] {{
--bg:#121212; --fg:#eee; --card:#1f1f1f; --table:#333;
}}
body{{font-family:Arial;background:var(--bg);color:var(--fg);padding:20px}}
button{{padding:6px 12px}}
.cards{{display:flex;gap:10px;margin:10px 0}}
.card{{background:var(--card);padding:10px;border-radius:6px;min-width:120px;text-align:center}}
.card.critical{{border-left:6px solid #d32f2f}}
.card.high{{border-left:6px solid #f57c00}}
.card.medium{{border-left:6px solid #fbc02d}}
.card.low{{border-left:6px solid #388e3c}}
table{{width:100%;border-collapse:collapse}}
th,td{{border:1px solid var(--table);padding:8px;word-break:break-all}}
th{{background:#444;color:#fff}}
code{{background:#0002;padding:2px 4px}}
</style>
</head>
<body>
<button onclick="toggle()">🌙 Toggle Dark Mode</button>
<h2>linuxcmdscan Report</h2>
<div class="cards">
{card("critical")}{card("high")}{card("medium")}{card("low")}
</div>
<table>
<tr><th>File</th><th>Line</th><th>Command</th><th>Severity</th><th>Content</th></tr>
{rows}
</table>
<script>
function toggle(){{
let d=document.documentElement;
let t=d.getAttribute("data-theme")==="dark"?"light":"dark";
d.setAttribute("data-theme",t);
localStorage.setItem("theme",t);
}}
let s=localStorage.getItem("theme");
if(s)document.documentElement.setAttribute("data-theme",s);
</script>
</body></html>""")