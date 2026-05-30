import os
import yaml
from github import Github, Auth

GITHUB_TOKEN = "YOUR_TOKEN_HERE"

REPOS = [
    "stripe/stripe-python",
    "django/djangoproject.com",
    "pubkey/broadcast-channel",
    "nashtech-garage/yas",
    "sparrowwallet/sparrow",
]

def analyse_workflow(content, filename):
    try:
        wf = yaml.safe_load(content)
    except Exception as e:
        return {"error": str(e)}

    if not wf or "jobs" not in wf:
        return {"error": "No jobs found"}

    jobs = wf.get("jobs", {})
    analysis = {
        "filename": filename,
        "job_count": len(jobs),
        "jobs": {},
        "has_caching": False,
        "has_matrix": False,
        "has_sequential_deps": False,
        "caching_opportunities": [],
        "parallelization_opportunities": [],
    }

    for job_name, job_config in jobs.items():
        if not isinstance(job_config, dict):
            continue

        job_info = {
            "runs_on": job_config.get("runs-on", "unknown"),
            "needs": job_config.get("needs", []),
            "has_matrix": "matrix" in str(job_config.get("strategy", {})),
            "steps": [],
            "uses_cache": False,
            "installs_deps": False,
        }

        if job_info["needs"]:
            analysis["has_sequential_deps"] = True

        if job_info["has_matrix"]:
            analysis["has_matrix"] = True

        steps = job_config.get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue

            step_name = step.get("name", step.get("uses", "unnamed"))
            uses = step.get("uses", "")
            run = step.get("run", "")

            if "actions/cache" in uses:
                job_info["uses_cache"] = True
                analysis["has_caching"] = True

            if "cache" in str(step).lower() and ("actions/cache" in uses or "cache:" in str(step)):
                job_info["uses_cache"] = True
                analysis["has_caching"] = True

            dep_keywords = ["pip install", "npm install", "npm ci", "yarn install",
                          "mvn ", "gradle ", "maven", "composer install",
                          "bundle install", "go mod download"]
            for kw in dep_keywords:
                if kw in run.lower():
                    job_info["installs_deps"] = True
                    if not job_info["uses_cache"]:
                        analysis["caching_opportunities"].append(
                            f"Job '{job_name}': runs '{kw}' without caching"
                        )

            job_info["steps"].append(step_name[:60])

        analysis["jobs"][job_name] = job_info

    if analysis["has_sequential_deps"]:
        for job_name, job_info in analysis["jobs"].items():
            needs = job_info["needs"]
            if needs:
                needs_list = needs if isinstance(needs, list) else [needs]
                analysis["parallelization_opportunities"].append(
                    f"Job '{job_name}' depends on {needs_list}"
                )

    if not analysis["has_matrix"]:
        for job_name, job_info in analysis["jobs"].items():
            analysis["parallelization_opportunities"].append(
                f"Job '{job_name}' has no matrix strategy"
            )

    return analysis


def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    output_dir = "workflow_analysis"
    os.makedirs(output_dir, exist_ok=True)

    for repo_name in REPOS:
        print(f"\nREPO: {repo_name}")

        repo = g.get_repo(repo_name)

        try:
            workflow_files = repo.get_contents(".github/workflows")
        except Exception as e:
            print(f"  Could not access workflows: {e}")
            continue

        yml_files = [f for f in workflow_files if f.name.endswith(('.yml', '.yaml'))]

        for wf_file in yml_files:
            content = wf_file.decoded_content.decode('utf-8')

            safe_name = repo_name.replace("/", "_")
            filepath = os.path.join(output_dir, f"{safe_name}_{wf_file.name}")
            with open(filepath, "w") as f:
                f.write(content)

            analysis = analyse_workflow(content, wf_file.name)

            if "error" in analysis:
                print(f"  [{wf_file.name}] Error: {analysis['error']}")
                continue

            print(f"\n  [{wf_file.name}]")
            print(f"    Jobs: {analysis['job_count']}")
            print(f"    Has caching: {'YES' if analysis['has_caching'] else 'NO'}")
            print(f"    Has matrix: {'YES' if analysis['has_matrix'] else 'NO'}")
            print(f"    Has sequential deps: {'YES' if analysis['has_sequential_deps'] else 'NO'}")

            for job_name, job_info in analysis["jobs"].items():
                needs_str = f" (needs: {job_info['needs']})" if job_info['needs'] else ""
                matrix_str = " [MATRIX]" if job_info['has_matrix'] else ""
                cache_str = " [CACHED]" if job_info['uses_cache'] else ""
                deps_str = " [INSTALLS DEPS]" if job_info['installs_deps'] else ""
                print(f"    - {job_name}{needs_str}{matrix_str}{cache_str}{deps_str}")

            if analysis["caching_opportunities"]:
                print(f"    CACHING OPPORTUNITIES:")
                for opp in analysis["caching_opportunities"]:
                    print(f"       - {opp}")

            if analysis["parallelization_opportunities"]:
                print(f"    PARALLELIZATION OPPORTUNITIES:")
                for opp in analysis["parallelization_opportunities"]:
                    print(f"       - {opp}")

    print(f"\nAll workflow YAML files saved to: {output_dir}/")


if __name__ == "__main__":
    main()