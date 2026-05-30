import csv
import time
from datetime import datetime, timedelta
from github import Github, Auth

GITHUB_TOKEN = "YOUR_TOKEN_HERE"

MIN_STARS = 100
MAX_STARS = 2000
MIN_WORKFLOW_RUNS = 50
LANGUAGES = ["Python", "JavaScript", "Java"]
REPOS_PER_LANGUAGE = 10

def get_rate_remaining(g):
    try:
        rate = g.get_rate_limit()
        if hasattr(rate, 'core'):
            return rate.core.remaining
        else:
            return rate.rate.remaining
    except Exception:
        return 999

def check_has_caching(workflow_contents):
    content_lower = workflow_contents.lower()
    return "actions/cache" in content_lower or "cache:" in content_lower

def check_has_parallelization(workflow_contents):
    content_lower = workflow_contents.lower()
    job_count = content_lower.count("jobs:")
    has_matrix = "matrix" in content_lower
    return job_count > 0, has_matrix

def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    print(f"Authenticated as: {g.get_user().login}")
    print(f"Rate limit remaining: {get_rate_remaining(g)}")

    six_months_ago = datetime.now() - timedelta(days=180)
    results = []

    for lang in LANGUAGES:
        print(f"\nSearching for {lang} repositories ({MIN_STARS}-{MAX_STARS} stars)...")

        query = f"language:{lang} stars:{MIN_STARS}..{MAX_STARS} pushed:>{six_months_ago.strftime('%Y-%m-%d')}"
        repos = g.search_repositories(query=query, sort="stars", order="desc")

        count = 0
        checked = 0
        for repo in repos:
            if count >= REPOS_PER_LANGUAGE:
                break
            if checked >= 60:
                break
            checked += 1

            try:
                print(f"Checking: {repo.full_name} ({repo.stargazers_count} stars)...")

                try:
                    workflows = list(repo.get_workflows())
                except Exception:
                    continue

                if len(workflows) == 0:
                    continue

                try:
                    runs = repo.get_workflow_runs()
                    total_runs = runs.totalCount
                except Exception:
                    total_runs = 0

                if total_runs < MIN_WORKFLOW_RUNS:
                    continue

                try:
                    workflow_files = repo.get_contents(".github/workflows")
                    yml_files = [f for f in workflow_files if f.name.endswith(('.yml', '.yaml'))]
                    yml_names = [f.name for f in yml_files]
                except Exception:
                    yml_files = []
                    yml_names = []

                if len(yml_files) == 0:
                    continue

                uses_caching = False
                has_multiple_jobs = False
                has_matrix = False

                try:
                    for wf in yml_files[:3]:
                        content = wf.decoded_content.decode('utf-8')
                        if check_has_caching(content):
                            uses_caching = True
                        jobs_check, matrix_check = check_has_parallelization(content)
                        if jobs_check:
                            has_multiple_jobs = True
                        if matrix_check:
                            has_matrix = True
                except Exception:
                    pass

                recent_runs = []
                try:
                    for run in repo.get_workflow_runs(status="completed"):
                        if run.conclusion == "success" and len(recent_runs) < 5:
                            duration = (run.updated_at - run.created_at).total_seconds()
                            recent_runs.append(duration)
                        if len(recent_runs) >= 5:
                            break
                except Exception:
                    pass

                avg_duration = sum(recent_runs) / len(recent_runs) if recent_runs else 0

                if avg_duration < 10 and avg_duration > 0:
                    continue

                repo_info = {
                    "name": repo.full_name,
                    "language": lang,
                    "stars": repo.stargazers_count,
                    "total_workflow_runs": total_runs,
                    "workflow_count": len(workflows),
                    "workflow_files": ", ".join(yml_names[:5]),
                    "uses_caching": "Yes" if uses_caching else "No",
                    "has_matrix_builds": "Yes" if has_matrix else "No",
                    "last_pushed": repo.pushed_at.strftime("%Y-%m-%d"),
                    "avg_build_time_seconds": round(avg_duration, 1),
                    "url": repo.html_url,
                    "description": (repo.description or "")[:100]
                }

                results.append(repo_info)
                count += 1

                remaining = get_rate_remaining(g)
                if remaining < 100:
                    print(f"Rate limit low ({remaining}), waiting 60 seconds...")
                    time.sleep(60)

            except Exception as e:
                print(f"Error: {e}")
                continue

    output_file = "stage1_candidate_repos_v2.csv"
    if results:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\nTotal candidate repositories found: {len(results)}")
        for lang in LANGUAGES:
            lang_repos = [r for r in results if r["language"] == lang]
            print(f"\n{lang}: {len(lang_repos)} repos found")
            for r in lang_repos:
                print(f"  - {r['name']} | {r['stars']} stars | {r['total_workflow_runs']} runs | avg build: {r['avg_build_time_seconds']}s")

        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()