import csv
import time
from github import Github, Auth

GITHUB_TOKEN = "YOUR_TOKEN_HERE"

REPOS = {
    "stripe/stripe-python": ["ci.yml"],
    "django/djangoproject.com": ["tests.yml"],
    "pubkey/broadcast-channel": ["main.yml"],
    "nashtech-garage/yas": ["cart-ci.yaml", "product-ci.yaml", "order-ci.yaml", "customer-ci.yaml", "inventory-ci.yaml"],
    "sparrowwallet/sparrow": ["package.yaml"],
}

MIN_RUNS = 30

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

    print(f"Authenticated as: {g.get_user().login}")
    print(f"Rate limit remaining: {get_rate_remaining(g)}")

    all_results = []

    for repo_name, workflow_files in REPOS.items():
        print(f"\n{repo_name}")

        repo = g.get_repo(repo_name)

        for wf_name in workflow_files:
            print(f"  Workflow: {wf_name}")

            target_workflow = None
            try:
                for wf in repo.get_workflows():
                    if wf.path.endswith(wf_name):
                        target_workflow = wf
                        break
            except Exception:
                continue

            if not target_workflow:
                continue

            collected = 0
            try:
                runs = target_workflow.get_runs(status="completed")
                for run in runs:
                    if collected >= MIN_RUNS:
                        break
                    if run.conclusion != "success":
                        continue

                    total_duration = (run.updated_at - run.created_at).total_seconds()

                    jobs_info = []
                    try:
                        jobs = run.jobs()
                        for job in jobs:
                            if job.completed_at and job.started_at:
                                duration = (job.completed_at - job.started_at).total_seconds()
                                jobs_info.append({"name": job.name, "duration": round(duration, 1)})
                    except Exception:
                        pass

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

                    remaining = get_rate_remaining(g)
                    if remaining < 50:
                        time.sleep(60)

            except Exception as e:
                print(f"    Error: {e}")

            print(f"    Collected: {collected} runs")

    output_file = "stage2_baseline_data.csv"
    if all_results:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)

        print(f"\nTotal records: {len(all_results)}")

        for repo_name in REPOS:
            repo_records = [r for r in all_results if r["repository"] == repo_name]
            if repo_records:
                durations = [r["total_duration_seconds"] for r in repo_records]
                avg = sum(durations) / len(durations)
                sorted_d = sorted(durations)
                median = sorted_d[len(sorted_d)//2]
                variance = sum((d - avg)**2 for d in durations) / len(durations)
                std_dev = variance ** 0.5
                print(f"\n{repo_name}: {len(repo_records)} runs, mean={avg:.1f}s, median={median:.1f}s, std={std_dev:.1f}s")

        print(f"\nData saved to: {output_file}")

if __name__ == "__main__":
    main()