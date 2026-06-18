"""
============================================================
 E-Commerce BI & Sales Prediction Platform
 Script 00 — Master Pipeline Runner
 Executes all scripts in sequence with timing & summary
============================================================
 Usage:
   python3 Python/00_run_all.py
   python3 Python/00_run_all.py --skip-dataset   (if CSV already exists)
============================================================
"""

import os
import sys
import time
import subprocess
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║   E-COMMERCE BUSINESS INTELLIGENCE & SALES PREDICTION       ║
║   PLATFORM — FULL PIPELINE RUNNER                           ║
║   Author : Data Analytics Team                              ║
╚══════════════════════════════════════════════════════════════╝
"""

CYAN   = "\033[96m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

SCRIPTS = [
    ("00 — Generate Dataset",       "Python/generate_dataset.py",       True),
    ("01 — Data Cleaning",          "Python/01_data_cleaning.py",        False),
    ("02 — Customer Segmentation",  "Python/02_customer_segmentation.py",False),
    ("03 — Predictive Analytics",   "Python/03_predictive_analytics.py", False),
    ("04 — Executive Dashboard",    "Python/04_executive_dashboard.py",  False),
    ("05 — SQL Analytics Runner",   "Python/05_sql_analytics_runner.py", False),
]

def run_script(label, script_path, skip=False):
    full_path = os.path.join(BASE, script_path)
    if skip:
        print(f"  {YELLOW}⏭  SKIP  {RESET}{label}")
        return True, 0.0

    print(f"\n  {CYAN}▶  RUNNING{RESET}  {BOLD}{label}{RESET}")
    print(f"     {script_path}")
    print("  " + "─" * 58)

    start = time.time()
    result = subprocess.run(
        [sys.executable, full_path],
        capture_output=False,
        text=True,
        cwd=BASE
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n  {GREEN}✅  DONE{RESET}  {label}  [{elapsed:.1f}s]")
        return True, elapsed
    else:
        print(f"\n  {RED}❌  FAILED{RESET}  {label}  [{elapsed:.1f}s]")
        return False, elapsed

def main():
    print(CYAN + BANNER + RESET)
    print(f"  Start Time : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    print(f"  Project    : {BASE}")
    print(f"  Python     : {sys.version.split()[0]}")
    print()

    skip_dataset = "--skip-dataset" in sys.argv

    summary = []
    total_start = time.time()

    for label, script, is_gen in SCRIPTS:
        should_skip = is_gen and skip_dataset
        success, elapsed = run_script(label, script, should_skip)
        summary.append((label, success, elapsed, should_skip))

    total_elapsed = time.time() - total_start

    # ── Final Summary ─────────────────────────────────────
    print("\n\n" + "═"*65)
    print(f"  {'PIPELINE SUMMARY':^61}")
    print("═"*65)
    print(f"  {'Script':<40} {'Status':^10} {'Time':>8}")
    print("  " + "─"*60)

    passed = 0
    failed = 0
    for label, success, elapsed, skipped in summary:
        if skipped:
            status = f"{YELLOW}SKIPPED{RESET}"
        elif success:
            status = f"{GREEN}PASSED{RESET}"
            passed += 1
        else:
            status = f"{RED}FAILED{RESET}"
            failed += 1
        t = f"{elapsed:.1f}s" if not skipped else "—"
        print(f"  {label:<40} {status:^18} {t:>8}")

    print("  " + "─"*60)
    print(f"  Total Pipeline Time : {total_elapsed:.1f}s")
    print(f"  Passed : {passed}   Failed : {failed}")

    # ── Output Inventory ──────────────────────────────────
    print("\n  OUTPUT FILES GENERATED:")
    output_dirs = ["Dataset", "Reports", "SQL"]
    for d in output_dirs:
        full_d = os.path.join(BASE, d)
        if os.path.exists(full_d):
            files = os.listdir(full_d)
            print(f"\n  📁  {d}/")
            for f in sorted(files):
                size = os.path.getsize(os.path.join(full_d, f))
                size_str = f"{size/1024:.1f} KB" if size < 1e6 else f"{size/1e6:.2f} MB"
                print(f"      • {f:<45} {size_str:>10}")

    print("\n" + "═"*65)
    if failed == 0:
        print(f"  {GREEN}{BOLD}🎉  ALL SCRIPTS COMPLETED SUCCESSFULLY!{RESET}")
    else:
        print(f"  {RED}{BOLD}⚠️   {failed} SCRIPT(S) FAILED — CHECK OUTPUT ABOVE{RESET}")
    print("═"*65 + "\n")

if __name__ == "__main__":
    main()
