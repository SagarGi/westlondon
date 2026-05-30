"""
Stage 2: Baseline Data Collection
Dissertation - Build Time Optimization in GitHub Actions

Collects build times from the last 30+ successful workflow runs
for each selected repository BEFORE any optimizations are applied.

Run: python stage2_baseline_collection.py
"""

import csv
import time
from datetime import datetime
from github import Github, Auth

GITHUB_TOKEN = ""

# The 5 selected repos and their main CI workflow files
REPOS = {
    "stripe/stripe-python": ["ci.yml"],
    "django/djangoproject.com": ["tests.yml"],
    "pubkey/broadcast-channel": ["main.yml"],
    "nashtech-garage/yas": ["cart-ci.yaml", "product-ci.yaml", "order-ci.yaml", "customer-ci.yaml", "inventory-ci.yaml"],
    "sparrowwallet/sparrow": ["package.yaml"],
}

MIN_RUNS = 30  # minimum successful runs to collect per workflow

def get_rate_remaining(g):
    try:
        rate = g.get_rate_limit()
        if hasattr(rate, 'core'):
            return rate.core.remaining
        else:
            return rate.rate.remaining
    except Exception:
        return 999

def collect_job_durations(repo, run):
    """Get individual job durations for a workflow run"""
    jobs_info = []
    try:
        jobs = run.jobs()
        for job in jobs:
            if job.completed_at and job.started_at:
                duration = (job.completed_at - job.started_at).total_seconds()
                jobs_info.append({"name": job.name, "duration": round(duration, 1)})
    except Exception as e:
        pass
    return jobs_info

def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    print(f"Authenticated as: {g.get_user().login}")
    print(f"Rate limit remaining: {get_rate_remaining(g)}")
    print(f"\nCollecting baseline build data from {len(REPOS)} repositories...")
    print(f"Target: {MIN_RUNS} successful runs per workflow\n")

    all_results = []

    for repo_name, workflow_files in REPOS.items():
        print(f"\n{'='*60}")
        print(f"  {repo_name}")
        print(f"{'='*60}")

        repo = g.get_repo(repo_name)

        for wf_name in workflow_files:
            print(f"\n  Workflow: {wf_name}")

            # Find the workflow by filename
            target_workflow = None
            try:
                for wf in repo.get_workflows():
                    if wf.path.endswith(wf_name):
                        target_workflow = wf
                        break
            except Exception as e:
                print(f"    Error finding workflow: {e}")
                continue

            if not target_workflow:
                print(f"    Workflow not found, skipping")
                continue

            # Collect successful runs
            collected = 0
            try:
                runs = target_workflow.get_runs(status="completed")
                for run in runs:
                    if collected >= MIN_RUNS:
                        break

                    if run.conclusion != "success":
                        continue

                    # Calculate total duration
                    total_duration = (run.updated_at - run.created_at).total_seconds()

                    # Get job-level durations
                    jobs_info = collect_job_durations(repo, run)
                    jobs_str = "; ".join([f"{j['name']}={j['duration']}s" for j in jobs_info])

                    record = {
                        "repository": repo_name,
                        "workflow": wf_name,
                        "run_number": run.run_number,
                        "run_id": run.id,
                        "total_duration_seconds": round(total_duration, 1),
                        "job_count": len(jobs_info),
                        "job_durations": jobs_str,
                        "branch": run.head_branch,
                        "event": run.event,
                        "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "conclusion": run.conclusion,
                    }

                    all_results.append(record)
                    collected += 1

                    if collected % 10 == 0:
                        print(f"    Collected {collected}/{MIN_RUNS} runs...")

                    # Rate limit check
                    remaining = get_rate_remaining(g)
                    if remaining < 50:
                        print(f"    Rate limit low ({remaining}), waiting 60s...")
                        time.sleep(60)

            except Exception as e:
                print(f"    Error collecting runs: {e}")

            print(f"    Done: {collected} successful runs collected")

            # Quick stats
            if collected > 0:
                durations = [r["total_duration_seconds"] for r in all_results
                           if r["repository"] == repo_name and r["workflow"] == wf_name]
                avg = sum(durations) / len(durations)
                min_d = min(durations)
                max_d = max(durations)
                print(f"    Avg: {avg:.1f}s | Min: {min_d:.1f}s | Max: {max_d:.1f}s")

    # Save to CSV
    output_file = "stage2_baseline_data.csv"
    if all_results:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)

        print(f"\n\n{'='*60}")
        print(f"BASELINE DATA SUMMARY")
        print(f"{'='*60}")
        print(f"Total records: {len(all_results)}\n")

        for repo_name in REPOS:
            repo_records = [r for r in all_results if r["repository"] == repo_name]
            if repo_records:
                durations = [r["total_duration_seconds"] for r in repo_records]
                avg = sum(durations) / len(durations)
                sorted_d = sorted(durations)
                median = sorted_d[len(sorted_d)//2]
                variance = sum((d - avg)**2 for d in durations) / len(durations)
                std_dev = variance ** 0.5

                print(f"{repo_name}:")
                print(f"  Runs collected: {len(repo_records)}")
                print(f"  Mean:   {avg:.1f}s")
                print(f"  Median: {median:.1f}s")
                print(f"  Std Dev: {std_dev:.1f}s")
                print(f"  Min:    {min(durations):.1f}s")
                print(f"  Max:    {max(durations):.1f}s")
                print()

        print(f"Data saved to: {output_file}")
        print(f"\nNext step: Upload this CSV back to Claude!")
    else:
        print("\nNo data collected.")

if __name__ == "__main__":
    main()