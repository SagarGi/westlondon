"""
Stage 5: Collect Post-Optimization Data from stripe-python
Run: python stage5_collect_stripe.py
"""

import csv
import time
from github import Github, Auth

GITHUB_TOKEN = ""

FORK_REPO = "SagarGi/stripe-python"

def get_rate_remaining(g):
    try:
        rate = g.get_rate_limit()
        if hasattr(rate, 'core'):
            return rate.core.remaining
        else:
            return rate.rate.remaining
    except Exception:
        return 999

def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(FORK_REPO)

    print(f"Collecting data from: {FORK_REPO}")
    print(f"Rate limit remaining: {get_rate_remaining(g)}\n")

    # Get all completed workflow runs
    all_runs = []
    for run in repo.get_workflow_runs(status="completed"):
        if run.conclusion != "success":
            continue

        duration = (run.updated_at - run.created_at).total_seconds()

        # Skip stuck runs (> 1 hour)
        if duration > 3600:
            continue

        all_runs.append({
            "run_id": run.id,
            "run_number": run.run_number,
            "total_duration_seconds": round(duration, 1),
            "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "commit_message": (run.head_commit.message if run.head_commit else "")[:100],
            "event": run.event,
            "branch": run.head_branch,
        })

        if len(all_runs) >= 50:  # enough data
            break

    # Sort by created_at
    all_runs.sort(key=lambda x: x["created_at"])

    # Print all runs for review
    print(f"Found {len(all_runs)} successful runs:\n")
    print(f"{'#':<4} {'Run':<8} {'Duration(s)':<14} {'Created':<22} {'Event':<16} {'Commit Message'}")
    print("-" * 110)
    for i, r in enumerate(all_runs, 1):
        print(f"{i:<4} {r['run_number']:<8} {r['total_duration_seconds']:<14} {r['created_at']:<22} {r['event']:<16} {r['commit_message'][:50]}")

    # Save to CSV
    output_file = "stage5_stripe_post_optimization.csv"
    if all_runs:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_runs[0].keys())
            writer.writeheader()
            writer.writerows(all_runs)
        print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    main()
