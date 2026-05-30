"""
Collect Post-Optimization Data from nashtech-garage/yas
Run: python stage5_collect_yas.py
"""

import csv
from github import Github, Auth

GITHUB_TOKEN = ""
FORK_REPO = "SagarGi/yas"

def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(FORK_REPO)

    print(f"Collecting data from: {FORK_REPO}\n")

    all_runs = []
    for run in repo.get_workflow_runs(status="completed"):
        # Only cart-ci workflow
        if "cart" not in run.name.lower():
            continue

        duration = (run.updated_at - run.created_at).total_seconds()
        if duration > 3600:
            continue

        all_runs.append({
            "run_id": run.id,
            "run_number": run.run_number,
            "workflow": run.name,
            "total_duration_seconds": round(duration, 1),
            "conclusion": run.conclusion,
            "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "commit_message": (run.head_commit.message if run.head_commit else "")[:100],
            "event": run.event,
            "branch": run.head_branch,
        })

        if len(all_runs) >= 50:
            break

    all_runs.sort(key=lambda x: x["created_at"])

    print(f"Found {len(all_runs)} runs:\n")
    print(f"{'#':<4} {'Run':<8} {'Duration(s)':<14} {'Status':<10} {'Created':<22} {'Commit Message'}")
    print("-" * 110)
    for i, r in enumerate(all_runs, 1):
        print(f"{i:<4} {r['run_number']:<8} {r['total_duration_seconds']:<14} {r['conclusion']:<10} {r['created_at']:<22} {r['commit_message'][:45]}")

    output_file = "stage5_yas_post_optimization.csv"
    if all_runs:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_runs[0].keys())
            writer.writeheader()
            writer.writerows(all_runs)
        print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    main()