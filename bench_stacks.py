"""One task, the Python scraping stacks in STACKS, measured.

The task: collect 200 hockey-team rows from scrapethissite.com/pages/forms/ (a scraping
sandbox, 25 rows per page, so 8 sequential page fetches). Each stack lives in
impl/task_*.py, runs in its own fresh venv (built by deps_venvs.py) so imports and
cold start are honest, and prints {"rows": N} on success.

Per stack: RUNS wall-clock timings (median reported), peak RSS of the process tree
(polled every 50 ms), lines of code of the implementation (non-blank, non-comment,
probe block excluded), and one anti-bot probe (what a plain fetch of
stackoverflow.com/questions returns through that stack). Playwright's Chromium is
installed into its venv on first use. Writes results/bench.json incrementally.
"""
import json
import pathlib
import statistics
import subprocess
import sys
import threading
import time

import psutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = pathlib.Path(__file__).resolve().parent
S = HERE / "results"
S.mkdir(parents=True, exist_ok=True)
OUT = S / "bench.json"
VROOT = HERE / ".dep-venvs"
RUNS = 10

STACKS = {
    "requests-bs4": "task_requests_bs4.py",
    "requests-lxml": "task_requests_lxml.py",
    "httpx-parsel": "task_httpx_parsel.py",
    "curl_cffi-lxml": "task_curlcffi_lxml.py",
    "scrapy": "task_scrapy.py",
    "selenium": "task_selenium.py",
    "playwright": "task_playwright.py",
    "scrapy-playwright": "task_scrapy_playwright.py",
    "seleniumbase": "task_seleniumbase.py",
    "playwright-stealth": "task_playwright_stealth.py",
}


def loc(path):
    n = 0
    in_probe = False
    for line in path.read_text(encoding="utf-8").splitlines():
        st = line.strip()
        if 'sys.argv[1] == "probe"' in st:
            in_probe = True
        if in_probe:
            if st.startswith("raise SystemExit"):
                in_probe = False
            continue
        if st and not st.startswith("#"):
            n += 1
    return n


def run_once(py, script, arg=None):
    cmd = [str(py), str(script)] + ([arg] if arg else [])
    peak = {"rss": 0}
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace")

    def poll():
        try:
            root = psutil.Process(proc.pid)
            while proc.poll() is None:
                try:
                    procs = [root] + root.children(recursive=True)
                    rss = sum(p.memory_info().rss for p in procs if p.is_running())
                    peak["rss"] = max(peak["rss"], rss)
                except (psutil.Error, OSError):
                    # OSError: a transient WinError 1455 (paging file) under heavy
                    # browser load must not kill the sampler for the rest of the run
                    pass
                time.sleep(0.05)
        except psutil.Error:
            pass

    t = threading.Thread(target=poll)
    t.start()
    out_text, err_text = proc.communicate(timeout=600)
    wall = time.perf_counter() - t0
    t.join(timeout=2)
    result = None
    for line in out_text.strip().splitlines()[::-1]:
        try:
            result = json.loads(line)
            break
        except ValueError:
            continue
    return dict(wall=round(wall, 2), peak_mb=round(peak["rss"] / 1024 / 1024),
                result=result, rc=proc.returncode, err=err_text.strip()[-300:])


def main():
    state = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

    pw_py = VROOT / "playwright" / "Scripts" / "python.exe"
    if pw_py.exists() and not state.get("_pw_browser"):
        print("installing chromium into the playwright venv...")
        subprocess.run([str(pw_py), "-m", "playwright", "install", "chromium"],
                       capture_output=True, text=True)
        state["_pw_browser"] = True
        OUT.write_text(json.dumps(state, indent=1), encoding="utf-8")

    for name, script_name in STACKS.items():
        done = state.get(name, {})
        if done.get("runs_n", 0) + done.get("failures", 0) >= RUNS:
            continue
        py = VROOT / name / "Scripts" / "python.exe"
        script = HERE / "impl" / script_name
        runs, fails, last_err = [], 0, ""
        for i in range(RUNS):
            r = run_once(py, script)
            ok = r["rc"] == 0 and r["result"] and r["result"].get("rows") == 200
            if ok:
                runs.append(r)
            else:
                fails += 1
                last_err = r["err"] or str(r["result"])
                print(f"  {name} run {i+1} FAILED rc={r['rc']} {last_err[:120]}")
                if fails >= 3 and not runs:
                    break
            time.sleep(1)
        entry = dict(runs_n=len(runs), failures=fails, loc=loc(script), last_err=last_err[:200])
        if runs:
            entry["wall_median"] = round(statistics.median(r["wall"] for r in runs), 2)
            entry["peak_mb_median"] = round(statistics.median(r["peak_mb"] for r in runs))
            launches = [r["result"].get("launch_s") for r in runs if r["result"].get("launch_s")]
            entry["launch_median"] = round(statistics.median(launches), 2) if launches else None
        probe = run_once(py, script, "probe")
        entry["probe"] = (probe["result"] or {}).get("probe_status", f"rc={probe['rc']}")
        state[name] = entry
        OUT.write_text(json.dumps(state, indent=1), encoding="utf-8")
        print(name, "->", entry)

    print("saved bench.json")


if __name__ == "__main__":
    main()
