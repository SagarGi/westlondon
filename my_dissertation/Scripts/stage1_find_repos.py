"""
Stage 1: Repository Selection Script (v2 - Mid-sized repos)
Dissertation - Build Time Optimization in GitHub Actions

Targets normal, mid-sized repos (100-2000 stars) instead of mega-repos.
These are more realistic for your research and easier to analyse.

HOW TO RUN:
1. Install required library:   pip install PyGithub
2. Run the script:             python stage1_find_repos_v2.py
"""

import csv
import time
from datetime import datetime, timedelta
from github import Github, Auth

# ============================================================
# PUT YOUR GITHUB TOKEN HERE
# ============================================================
GITHUB_TOKEN = ""

# Selection criteria - targeting NORMAL mid-sized repos
MIN_STARS = 100
MAX_STARS = 2000
MIN_WORKFLOW_RUNS = 50
LANGUAGES = ["Python", "JavaScript", "Java"]
REPOS_PER_LANGUAGE = 10  # candidates per language

def get_rate_remaining(g):
    """Get remaining rate limit - works across PyGithub versions"""
    try:
        rate = g.get_rate_limit()
        if hasattr(rate, 'core'):
            return rate.core.remaining
        else:
            return rate.rate.remaining
    except Exception:
        return 999

def check_has_caching(workflow_contents):
    """Check if a workflow file uses caching"""
    content_lower = workflow_contents.lower()
    return "actions/cache" in content_lower or "cache:" in content_lower

def check_has_parallelization(workflow_contents):
    """Check if workflow has multiple jobs"""
    content_lower = workflow_contents.lower()
    # Count job definitions
    job_count = content_lower.count("jobs:") 
    # Check for matrix strategy
    has_matrix = "matrix" in content_lower
    return job_count > 0, has_matrix

def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    print(f"Authenticated as: {g.get_user().login}")
    print(f"Rate limit remaining: {get_rate_remaining(g)}\n")
    print("Looking for MID-SIZED repos (100-2000 stars) - real world projects")
    print("These are much better for your dissertation than mega-repos!\n")

    six_months_ago = datetime.now() - timedelta(days=180)
    results = []

    for lang in LANGUAGES:
        print(f"\n{'='*60}")
        print(f"Searching for {lang} repositories (100-2000 stars)...")
        print(f"{'='*60}")

        # Search for mid-sized repos
        query = f"language:{lang} stars:{MIN_STARS}..{MAX_STARS} pushed:>{six_months_ago.strftime('%Y-%m-%d')}"
        repos = g.search_repositories(query=query, sort="stars", order="desc")

        count = 0
        checked = 0
        for repo in repos:
            if count >= REPOS_PER_LANGUAGE:
                break
            if checked >= 60:  # don't check too many
                break
            checked += 1

            try:
                print(f"\nChecking: {repo.full_name} ({repo.stargazers_count} stars)...")

                # Check if repo has GitHub Actions workflows
                try:
                    workflows = list(repo.get_workflows())
                except Exception:
                    print(f"  -> No workflows found, skipping")
                    continue

                if len(workflows) == 0:
                    print(f"  -> No workflows found, skipping")
                    continue

                # Check workflow runs count
                try:
                    runs = repo.get_workflow_runs()
                    total_runs = runs.totalCount
                except Exception:
                    total_runs = 0

                if total_runs < MIN_WORKFLOW_RUNS:
                    print(f"  -> Only {total_runs} workflow runs (need {MIN_WORKFLOW_RUNS}+), skipping")
                    continue

                # Check for workflow YAML files
                try:
                    workflow_files = repo.get_contents(".github/workflows")
                    yml_files = [f for f in workflow_files if f.name.endswith(('.yml', '.yaml'))]
                    yml_names = [f.name for f in yml_files]
                except Exception:
                    yml_files = []
                    yml_names = []

                if len(yml_files) == 0:
                    print(f"  -> No YAML workflow files found, skipping")
                    continue

                # Read workflow content to check for caching and parallelization
                uses_caching = False
                has_multiple_jobs = False
                has_matrix = False
                main_workflow_content = ""

                try:
                    for wf in yml_files[:3]:  # check first 3 workflow files
                        content = wf.decoded_content.decode('utf-8')
                        if not main_workflow_content:
                            main_workflow_content = content
                        if check_has_caching(content):
                            uses_caching = True
                        jobs_check, matrix_check = check_has_parallelization(content)
                        if jobs_check:
                            has_multiple_jobs = True
                        if matrix_check:
                            has_matrix = True
                except Exception as e:
                    print(f"  -> Could not read workflow content: {e}")

                # Get recent successful runs for build time
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

                # Skip repos with very short build times (< 10s) - not interesting
                if avg_duration < 10 and avg_duration > 0:
                    print(f"  -> Build time too short ({avg_duration:.0f}s), skipping")
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

                cache_status = "HAS caching" if uses_caching else "NO caching"
                matrix_status = "HAS matrix" if has_matrix else "no matrix"
                print(f"  -> MATCH! {total_runs} runs | avg build: {avg_duration:.0f}s | {cache_status} | {matrix_status}")

                # Respect rate limits
                remaining = get_rate_remaining(g)
                if remaining < 100:
                    print(f"\n  Rate limit low ({remaining}), waiting 60 seconds...")
                    time.sleep(60)

            except Exception as e:
                print(f"  -> Error: {e}")
                continue

    # Save results to CSV
    output_file = "stage1_candidate_repos_v2.csv"
    if results:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\n\n{'='*60}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total candidate repositories found: {len(results)}\n")

        for lang in LANGUAGES:
            lang_repos = [r for r in results if r["language"] == lang]
            print(f"\n{lang}: {len(lang_repos)} repos found")
            for r in lang_repos:
                cache_icon = "✓" if r["uses_caching"] == "Yes" else "✗"
                matrix_icon = "✓" if r["has_matrix_builds"] == "Yes" else "✗"
                print(f"  - {r['name']}")
                print(f"    {r['stars']} stars | {r['total_workflow_runs']} runs | avg build: {r['avg_build_time_seconds']}s")
                print(f"    Cache: {cache_icon} | Matrix: {matrix_icon}")

        # Summary of optimization opportunities
        no_cache = [r for r in results if r["uses_caching"] == "No"]
        no_matrix = [r for r in results if r["has_matrix_builds"] == "No"]
        print(f"\n\nOPTIMIZATION OPPORTUNITIES:")
        print(f"  Repos WITHOUT caching: {len(no_cache)} (can test caching optimization)")
        print(f"  Repos WITHOUT matrix builds: {len(no_matrix)} (can test parallelization)")

        print(f"\nResults saved to: {output_file}")
        print(f"\nNext step: Upload this CSV back to Claude to pick the final repos!")
    else:
        print("\nNo matching repositories found.")

if __name__ == "__main__":
    main()