"""Corpus-wide case_name contamination audit.

Two authorities, in priority:
  1. the court's opinion-report spreadsheet Title (joined by neutral or N.W. cite)
  2. the opinion's own body caption (the court's published caption)

For each opinion we ask: does `case_name` AGREE with the authority? Agreement =
exact normalized match OR a shared distinctive party surname. Disagreement is
flagged. Anonymized captions ("Interest of A.F.L.", "(CONFIDENTIAL)") match
trivially by the exact-normalized test, so they don't false-positive.
"""
from __future__ import annotations
import re, sqlite3, sys, csv
from pathlib import Path
import openpyxl
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.refs_diff import strip_frontmatter

STOP = {
    "state","north","dakota","city","county","interest","matter","estate","the",
    "and","et","al","inc","co","company","corp","corporation","llc","llp","ltd",
    "life","insurance","group","trust","bank","department","commission","bureau",
    "petition","discipline","disciplinary","board","application","reinstatement",
    "against","member","bar","supreme","court","confidential","personal",
    "representative","deceased","plaintiff","defendant","appellant","appellee",
    "petitioner","respondent","fka","aka","nka","dba","minor","child","children",
    "director","transportation","workforce","safety","public","school","district",
    "village","township","association","unknown","heirs","various","john","jane","doe",
}
def norm(s): return re.sub(r"[^a-z0-9]+"," ",(s or "").lower()).strip()
def surnames(s):
    return {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z'’-]{3,}", s or "")
            if t.lower() not in STOP}
def agree(name, authority):
    if not authority: return None
    if norm(name) == norm(authority): return True
    a,b = surnames(name), surnames(authority)
    if not a or not b: return norm(name)==norm(authority)
    return len(a & b) > 0

def body_caption(body):
    cap=[]
    for l in [x for x in body.splitlines() if x.strip()]:
        if re.search(r"North Dakota Supreme Court|^\s*No\.\s|Supreme Court Nos?|"
                     r"^\s*\d{4} ND \d+|Filed |Per Curiam|, (?:Justice|J\.|C\.J\.)", l): break
        cap.append(re.sub(r"^#\s*","",l).strip())
    return " ".join(cap)[:200]

# load spreadsheet
wb=openpyxl.load_workbook("input-data/court-opinions-report-2026-05-30.xlsx", read_only=True, data_only=True)
ws=wb.active; it=ws.iter_rows(values_only=True); next(it); next(it)
def nn(x): return re.sub(r"[ .]","",str(x)).upper() if x else None
sheet={}
for r in it:
    r=list(r)+[None]*(10-len(r)); _,title,_,_,_,_,nd1,nd2,nw1,nw2=r[:10]
    for c in (nd1,nd2,nw1,nw2):
        if c: sheet.setdefault(nn(c),title)

def _cite(cl):
    for rep,c in cl:
        if rep=="ND-neutral": return c
    return cl[0][1] if cl else ""

conn=sqlite3.connect("opinions.db"); conn.row_factory=sqlite3.Row
cites={}
for r in conn.execute("SELECT opinion_id, citation, reporter FROM citations"):
    cites.setdefault(r["opinion_id"],[]).append((r["reporter"],r["citation"]))

flags=[]; checked_sheet=0; checked_cap=0
for op in conn.execute("SELECT id, case_name, text_content FROM opinions"):
    oid=op["id"]; cn=op["case_name"]
    cl=cites.get(oid,[])
    # authoritative court Title via cite
    title=None
    for rep,c in cl:
        title=sheet.get(nn(c))
        if title: break
    body=strip_frontmatter(op["text_content"] or "")
    if title is not None:
        checked_sheet+=1
        if agree(cn,title) is False:
            flags.append((oid,_cite(cl),cn,title,"spreadsheet",body_caption(body)))
    else:
        # fall back to body caption
        cap=body_caption(body)
        checked_cap+=1
        sn=surnames(cn)
        if sn and not (sn & surnames(body)):   # no case_name surname anywhere in body
            flags.append((oid,_cite(cl),cn,cap,"caption",cap))
conn.close()
print(f"checked vs spreadsheet: {checked_sheet}, vs caption: {checked_cap}")
print(f"FLAGS: {len(flags)}  (spreadsheet-disagree: {sum(1 for f in flags if f[4]=='spreadsheet')}, "
      f"caption-disagree: {sum(1 for f in flags if f[4]=='caption')})")
with open("triage/casename-audit.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["oid","cite","case_name","authority_title","via","body_caption"])
    w.writerows(sorted(flags,key=lambda x:(x[4],x[1])))
print("wrote triage/casename-audit.csv")
for f in sorted(flags,key=lambda x:(x[4],str(x[1])))[:30]:
    print(f"  {f[0]} [{f[4]:<11}] {str(f[1]):<13} {f[2][:30]:<31} | auth: {str(f[3])[:40]}")
