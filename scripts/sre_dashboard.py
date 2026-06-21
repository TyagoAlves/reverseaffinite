import subprocess
import json
import os
import sys
from datetime import datetime, timezone

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO_DIR, "docs", "sre_dashboard.html")
AGENTS_FILE = os.path.join(REPO_DIR, "AGENTS.md")
REVERSE_FILE = os.path.join(REPO_DIR, "reverse.txt")


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_DIR, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def get_git_log(count=15):
    log = run(["git", "log", f"--max-count={count}", "--pretty=format:%h|%ai|%s"])
    commits = []
    for line in log.split("\n"):
        if "|" in line:
            parts = line.split("|", 2)
            commits.append({"hash": parts[0], "date": parts[1], "message": parts[2]})
    return commits


def get_branch():
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"])


def get_remote_url():
    url = run(["git", "config", "--get", "remote.origin.url"])
    return url.replace("https://", "").split("@")[-1] if "@" in url else url


def get_file_count():
    total = 0
    for root, dirs, files in os.walk(REPO_DIR):
        if ".git" in root or "__pycache__" in root:
            continue
        total += len(files)
    return total


def get_py_line_count():
    total = 0
    for root, dirs, files in os.walk(REPO_DIR):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    total += len(open(path, "rb").readlines())
                except Exception:
                    pass
    return total


def get_reverse_status():
    if not os.path.exists(REVERSE_FILE):
        return "No reverse.txt found"
    with open(REVERSE_FILE) as f:
        return f.read()


def count_tasks(txt):
    done = txt.count("Tasks Done")
    prog = txt.count("Tasks In Progress")
    todo = txt.count("Tasks Todo")
    total_match = [l for l in txt.split("\n") if "tasks done" in l.lower()]
    if total_match:
        import re
        m = re.search(r"(\d+)/(\d+)", total_match[0])
        if m:
            return int(m.group(1)), int(m.group(2)), done, prog, todo
    return 0, 0, done, prog, todo


def html_page(branch, commits, remote, files, py_lines, status):
    done, total_tasks, _, _, _ = count_tasks(status)
    pct = (done / total_tasks * 100) if total_tasks else 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_rows = ""
    for c in commits:
        commit_rows += f"<tr><td>{c['hash']}</td><td>{c['date']}</td><td>{c['message']}</td></tr>"
    status_html = status.replace("\n", "<br>") if status else "No status"
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
  .status {{ font-size: 13px; line-height: 1.6; }}
  .timestamp {{ color: #8b949e; font-size: 12px; text-align: right; margin-top: 16px; }}
  a {{ color: #58a6ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>reverseaffinity — SRE Dashboard</h1>

<div class="grid">
  <div class="stat"><div class="stat-value">{pct:.0f}%</div><div class="stat-label">Sprint Progress</div></div>
  <div class="stat"><div class="stat-value">{files}</div><div class="stat-label">Files</div></div>
  <div class="stat"><div class="stat-value">{py_lines:,}</div><div class="stat-label">Python Lines</div></div>
  <div class="stat"><div class="stat-value">{total_tasks}</div><div class="stat-label">Sprint Tasks</div></div>
</div>

<div class="progress-bar"><div class="progress-fill" style="width: {pct}%"></div></div>
<br>

<div class="grid">
  <div class="stat"><div class="stat-value">{done}</div><div class="stat-label">Done</div></div>
  <div class="stat"><div class="stat-value">{len(commits)}</div><div class="stat-label">Recent Commits</div></div>
  <div class="stat"><div class="stat-value">{branch}</div><div class="stat-label">Branch</div></div>
  <div class="stat"><div class="stat-value">{remote}</div><div class="stat-label">Remote</div></div>
</div>

<div class="card">
  <h2>Recent Commits</h2>
  <table><thead><tr><th>Hash</th><th>Date</th><th>Message</th></tr></thead><tbody>{commit_rows}</tbody></table>
</div>

<div class="card">
  <h2>Status</h2>
  <div class="status">{status_html}</div>
</div>

<div class="timestamp">Generated: {now}</div>
</body>
</html>"""


def main():
    print("Generating SRE dashboard...")
    branch = get_branch()
    commits = get_git_log()
    remote = get_remote_url()
    files = get_file_count()
    py_lines = get_py_line_count()
    status = get_reverse_status()
    html = html_page(branch, commits, remote, files, py_lines, status)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Dashboard written to {OUTPUT}")


if __name__ == "__main__":
    main()
