import subprocess
import json
import os
import re
from datetime import datetime, timezone

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO_DIR, "docs", "sre_dashboard.html")

ALL_REPOS = {
    "reverseaffinity (monorepo)": os.path.join(REPO_DIR),
    "reverseaffinity-video": os.path.join(os.path.dirname(REPO_DIR), "reverseaffinity-video"),
    "reverseaffinity-photo": os.path.join(os.path.dirname(REPO_DIR), "reverseaffinity-photo"),
    "reverseaffinity-effects": os.path.join(os.path.dirname(REPO_DIR), "reverseaffinity-effects"),
    "CineCPP-Core": os.path.join(os.path.dirname(REPO_DIR), "CineCPP-Core"),
    "opencode-lite": os.path.join(os.path.dirname(REPO_DIR), "opencode-lite"),
}


def run(cmd, cwd=None, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or REPO_DIR, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def check_repo(name, path):
    if not os.path.isdir(os.path.join(path, ".git")):
        return {"name": name, "status": "missing", "last_commit": "", "branch": "", "ahead": ""}
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
    remote = run(["git", "config", "--get", "remote.origin.url"], cwd=path)
    remote = remote.replace("https://", "").split("@")[-1] if "@" in remote else remote
    last = run(["git", "log", "-1", "--pretty=format:%h|%ai|%s"], cwd=path)
    parts = last.split("|") if "|" in last else ["", "", ""]
    ahead = run(["git", "rev-list", "--count", f"origin/{branch}..HEAD"], cwd=path) if branch else ""
    status = run(["git", "status", "--porcelain"], cwd=path)
    modified = len([l for l in status.split("\n") if l.strip()]) if status else 0
    return {
        "name": name,
        "status": "ok",
        "branch": branch,
        "remote": remote,
        "last_hash": parts[0],
        "last_date": parts[1],
        "last_msg": parts[2],
        "ahead": ahead or "0",
        "modified": modified,
    }


def get_reverse_status():
    f = os.path.join(REPO_DIR, "reverse.txt")
    if not os.path.exists(f):
        return ""
    with open(f) as fh:
        return fh.read()


def count_tasks(txt):
    m = re.search(r"(\d+)/(\d+)", txt)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 0, 0


def html_page(repos, rev_status):
    done, total = count_tasks(rev_status) if rev_status else (0, 0)
    pct = (done / total * 100) if total else 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    repo_rows = ""
    for r in repos:
        is_ok = r["status"] == "ok"
        badge = "🟢" if is_ok else "🔴"
        mod_badge = f" ✏️{r['modified']}" if r["modified"] > 0 else ""
        ahead_badge = f" ⬆{r['ahead']}" if r["ahead"] and r["ahead"] != "0" else ""
        repo_rows += f"""<tr>
          <td>{badge} {r['name']}{mod_badge}{ahead_badge}</td>
          <td>{r['branch']}</td>
          <td>{r['last_hash']}</td>
          <td>{r['last_date']}</td>
          <td>{r['last_msg']}</td>
        </tr>"""

    status_html = rev_status.replace("\n", "<br>") if rev_status else "No status"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SRE Dashboard — reverseaffinity</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
  .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 16px; }}
  h1 {{ color: #58a6ff; font-size: 24px; margin-bottom: 16px; }}
  h1 small {{ color: #8b949e; font-size: 14px; font-weight: normal; }}
  h2 {{ color: #8b949e; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px; }}
  .stat {{ background: #1c2128; border-radius: 6px; padding: 16px; text-align: center; }}
  .stat-value {{ font-size: 32px; font-weight: bold; color: #58a6ff; }}
  .stat-label {{ font-size: 12px; color: #8b949e; margin-top: 4px; }}
  .progress-bar {{ background: #30363d; border-radius: 10px; height: 12px; overflow: hidden; margin-top: 8px; }}
  .progress-fill {{ background: linear-gradient(90deg, #58a6ff, #1f6feb); height: 100%; border-radius: 10px; transition: width 0.5s; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #21262d; font-size: 13px; }}
  th {{ color: #8b949e; font-weight: 600; }}
  td {{ font-family: 'SF Mono', 'Consolas', monospace; }}
  .repo-ok {{ color: #3fb950; }} .repo-err {{ color: #f85149; }}
  .status {{ font-size: 13px; line-height: 1.6; }}
  .timestamp {{ color: #8b949e; font-size: 12px; text-align: right; margin-top: 16px; }}
  a {{ color: #58a6ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>reverseaffinity <small>Ecosystem SRE Dashboard</small></h1>

<div class="grid">
  <div class="stat"><div class="stat-value">{pct:.0f}%</div><div class="stat-label">Sprint Progress</div></div>
  <div class="stat"><div class="stat-value">{len(repos)}</div><div class="stat-label">Repositories</div></div>
  <div class="stat"><div class="stat-value">{sum(1 for r in repos if r['status']=='ok')}</div><div class="stat-label">Healthy</div></div>
  <div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Sprint Tasks</div></div>
</div>

<div class="progress-bar"><div class="progress-fill" style="width: {pct}%"></div></div>
<br>

<div class="card">
  <h2>Repository Health</h2>
  <table><thead><tr><th>Repository</th><th>Branch</th><th>Hash</th><th>Last Commit</th><th>Message</th></tr></thead><tbody>{repo_rows}</tbody></table>
</div>

<div class="card">
  <h2>Sprint Status</h2>
  <div class="status">{status_html}</div>
</div>

<div class="timestamp">Generated: {now}</div>
</body>
</html>"""


def main():
    print("Generating SRE dashboard for all 6 repos...")
    repos = []
    for name, path in ALL_REPOS.items():
        r = check_repo(name, path)
        repos.append(r)
        print(f"  {r['name']}: {r['status']} {r['branch']} ({r['last_hash']})")

    rev_status = get_reverse_status()
    html = html_page(repos, rev_status)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"\nDashboard written to {OUTPUT}")


if __name__ == "__main__":
    main()
