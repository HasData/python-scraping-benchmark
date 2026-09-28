"""Runs every example the article quotes, each in its stack's own venv.

The article's code blocks are these files verbatim, so a pass here means the printed
snippets run as published. Writes results/examples_run.json.
"""
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = pathlib.Path(__file__).resolve().parent
S = HERE / "results"
VROOT = HERE / ".dep-venvs"

RUNS = {
    "ex_requests.py": "requests-bs4",
    "ex_httpx.py": "httpx-parsel",
    "ex_httpx_async.py": "httpx-parsel",
    "ex_urllib3.py": "requests-bs4",
    "ex_curlcffi.py": "curl_cffi-lxml",
    "ex_bs4.py": "requests-bs4",
    "ex_lxml.py": "requests-lxml",
    "ex_parsel.py": "httpx-parsel",
    "ex_playwright.py": "playwright",
    "ex_selenium.py": "selenium",
    "ex_scrapy.py": "scrapy",
    "ex_scrapy_playwright.py": "scrapy-playwright",
}

out = {}
for script, venv in RUNS.items():
    py = VROOT / venv / "Scripts" / "python.exe"
    r = subprocess.run([str(py), str(HERE / "examples" / script)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=240)
    out[script] = dict(rc=r.returncode, stdout=r.stdout.strip()[-200:],
                       stderr=r.stderr.strip()[-200:] if r.returncode else "")
    print(f"{script:<18} rc={r.returncode} {r.stdout.strip()[-90:]}")

(S / "examples_run.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
fails = [k for k, v in out.items() if v["rc"] != 0]
print("failures:", fails or "none")
