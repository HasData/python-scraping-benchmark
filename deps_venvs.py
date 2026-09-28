"""How many packages each scraping stack actually pulls in, measured in fresh venvs.

One venv per stack, pip install the stack, count everything beyond pip itself.
Also records the resolved version of each headline package. Writes results/deps.json.
"""
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
S = pathlib.Path(__file__).resolve().parent.parent / "study"
S.mkdir(parents=True, exist_ok=True)
VROOT = pathlib.Path(__file__).resolve().parent / ".dep-venvs"
VROOT.mkdir(exist_ok=True)

STACKS = {
    "requests-bs4": ["requests", "beautifulsoup4"],
    "requests-lxml": ["requests", "lxml"],
    "httpx-parsel": ["httpx", "parsel"],
    "curl_cffi-lxml": ["curl_cffi", "lxml"],
    "scrapy": ["scrapy"],
    "selenium": ["selenium"],
    "playwright": ["playwright"],
}

out = {}
for name, pkgs in STACKS.items():
    venv = VROOT / name
    py = venv / "Scripts" / "python.exe"
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    ins = subprocess.run([str(py), "-m", "pip", "install", "-q", *pkgs],
                         capture_output=True, text=True, encoding="utf-8")
    frz = subprocess.run([str(py), "-m", "pip", "list", "--format=freeze"],
                         capture_output=True, text=True, encoding="utf-8")
    lines = [l for l in frz.stdout.splitlines() if l and not l.lower().startswith("pip==")]
    versions = {l.split("==")[0]: l.split("==")[1] for l in lines
                if l.split("==")[0].lower().replace("_", "-") in
                [p.lower().replace("_", "-") for p in pkgs]}
    out[name] = dict(install_rc=ins.returncode, packages=len(lines),
                     headline=versions, all=sorted(lines))
    print(f"{name:<16} {len(lines):>3} packages, {versions}")

(S / "deps.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved deps.json")
