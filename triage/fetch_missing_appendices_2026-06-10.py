"""Stage 1 (run under ~/code/rules-scraper/.venv): fetch the N.D.R.Ct.
appendices missing from rules.db (c, d, e, l, m — present on the live index,
absent from the mirror repo and the DB) using the rules-scraper's own
extractor + HTML->markdown converter. Dumps JSON for stage 2 insertion.
"""
import json, sys, time
sys.path.insert(0, "/Users/jerod/code/rules-scraper/src")
import requests
from scraper.version_history_extractor import VersionHistoryExtractor
from scraper.historical_version_fetcher import HistoricalVersionFetcher

BASE = "https://www.ndcourts.gov/legal-resources/rules/ndrct"
SLUGS = ["appendix-c", "appendix-d", "appendix-e", "appendix-l", "appendix-m"]

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (rules mirror; jetcite project)"
extractor = VersionHistoryExtractor()
fetcher = HistoricalVersionFetcher(session, request_delay=1.0)

out = {}
for slug in SLUGS:
    url = f"{BASE}/{slug}"
    html = session.get(url, timeout=30).text
    hist = extractor.extract_version_history(html, url)
    versions = fetcher.fetch_all_versions(hist)
    out[slug] = {
        "title": hist.rule_title,
        "rule_number": hist.rule_number,
        "versions": [
            {
                "rule_title": v.rule_title,
                "effective_date": v.effective_date.isoformat() if v.effective_date else None,
                "obsolete_date": v.obsolete_date.isoformat() if v.obsolete_date else None,
                "is_current": v.is_current,
                "url": v.url,
                "markdown": v.markdown,
            }
            for v in versions
        ],
    }
    print(f"{slug}: {hist.rule_title!r} — {len(versions)} version(s) "
          f"{[v.effective_date.isoformat() if v.effective_date else None for v in versions]}",
          file=sys.stderr)
    time.sleep(1.0)

json.dump(out, open("/tmp/missing_appendices.json", "w"), indent=1)
print("wrote /tmp/missing_appendices.json", file=sys.stderr)
