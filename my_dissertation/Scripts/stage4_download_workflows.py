"""
Stage 4 Prep: Download workflow files from your forks
Run: python stage4_download_workflows.py
"""

import os
from github import Github, Auth

GITHUB_TOKEN = "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"

# Your fork username
FORK_USER = "SagarGi"

# Repos and their key workflow files to optimize
REPOS = {
    "stripe/stripe-python": ["ci.yml"],
    "django/djangoproject.com": ["tests.yml"],
    "nashtech-garage/yas": ["cart-ci.yaml", "product-ci.yaml", "order-ci.yaml"],
    "sparrowwallet/sparrow": ["package.yaml"],
}

def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    output_dir = "stage4_workflows"
    os.makedirs(output_dir, exist_ok=True)

    for repo_name, wf_files in REPOS.items():
        # Try fork first, fall back to original
        fork_name = f"{FORK_USER}/{repo_name.split('/')[1]}"
        try:
            repo = g.get_repo(fork_name)
            print(f"\nUsing fork: {fork_name}")
        except Exception:
            repo = g.get_repo(repo_name)
            print(f"\nFork not found, using original: {repo_name}")

        for wf_name in wf_files:
            try:
                content = repo.get_contents(f".github/workflows/{wf_name}")
                text = content.decoded_content.decode("utf-8")

                safe_repo = repo_name.replace("/", "_")
                filepath = os.path.join(output_dir, f"{safe_repo}__{wf_name}")
                with open(filepath, "w") as f:
                    f.write(text)

                print(f"  Downloaded: {wf_name} ({len(text)} chars)")
            except Exception as e:
                print(f"  Error downloading {wf_name}: {e}")

    print(f"\nAll files saved to: {output_dir}/")

if __name__ == "__main__":
    main()