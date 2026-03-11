# Dissertation Workflow: Step-by-Step Action Plan

**Topic:** An Empirical Analysis of Build Time Optimization Strategies in GitHub Actions  
**Student:** Sagar Gurung  
**Timeline:** March 2026 - May 2026

---

## Phase 1: Project Setup & Literature Review (March 1 - March 10)

### Week 1: March 1 - March 7

#### Day 1-2: Administrative Setup
- [x] Submit ethics approval form to university
- [x] Create a dedicated folder structure for your dissertation:
  ```
  dissertation/
  ├── 01_literature/
  ├── 02_data_collection/
  ├── 03_analysis/
  ├── 04_results/
  ├── 05_writing/
  └── 06_scripts/
  ```
- [x] Set up a GitHub repository for your dissertation project
- [x] Install required tools:
  - Python 3.x
  - VS Code or preferred IDE
  - Git

#### Day 3-5: Literature Review - Reading
- [x] Read and take notes on these key papers:
  1. Gallaba et al. (2022) - "Accelerating Continuous Integration by Caching Environments"
  2. Bouzenia & Pradel (2024) - "Resource Usage and Optimization Opportunities in GitHub Actions"
  3. Gallaba & McIntosh (2020) - "Use and Misuse of Continuous Integration Features"
  4. Shahin et al. (2017) - "Continuous Integration, Delivery and Deployment: A Systematic Review"
  5. Rostami Mazrae et al. (2023) - "On the usage, co-usage and migration of CI/CD tools"

- [x] For each paper, note down:
  - Main findings
  - Methodology used
  - How it relates to your research
  - Gaps you can address

#### Day 6-7: Literature Review - Writing
- [x] Write first draft of Literature Review chapter (aim for 1500-2000 words)
- [x] Organize by themes:
  - CI/CD overview and importance
  - GitHub Actions as a platform
  - Build optimization techniques (caching, parallelization)
  - Research gaps

### Week 2: March 8 - March 10

#### Day 8-9: Setup Development Environment
- [x] Create a GitHub Personal Access Token for API access:
  1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
  2. Generate new token with `repo` and `workflow` permissions
  3. Save token securely

- [x] Install Python libraries:
  ```bash
  pip install requests pandas matplotlib scipy seaborn pyyaml
  ```

- [x] Test GitHub API connection with a simple script

#### Day 10: Finalize Phase 1
- [x] Review and refine literature review draft
- [x] Prepare repository selection criteria document
- [x] Create a tracking spreadsheet for your progress

---

## Phase 2: Repository Selection & Tools (March 11 - March 17)

### Week 3: March 11 - March 17

#### Day 11-12: Build Repository Selection Script
- [ ] Write Python script to search GitHub repositories using API
- [ ] Apply selection criteria:
  - Uses GitHub Actions (.github/workflows/ folder exists)
  - At least 100 stars
  - At least 50 workflow runs in past 6 months
  - Primary language: JavaScript, Python, or Java
  - Actively maintained (commits in last 3 months)

#### Day 13-14: Find Candidate Repositories
- [ ] Run your selection script
- [ ] Create a shortlist of 15-20 candidate repositories
- [ ] For each candidate, manually check:
  - Does it have identifiable inefficiencies?
  - Is the workflow file readable and understandable?
  - Is the build process typical (not too unique)?

#### Day 15-16: Finalize Repository Selection
- [ ] Narrow down to final 5-10 repositories
- [ ] Document each selected repository:
  - Repository name and URL
  - Primary language
  - Number of stars
  - Number of workflow runs
  - Current workflow configuration summary
  - Identified inefficiencies

#### Day 17: Build Data Collection Tools
- [ ] Write script to download workflow files (.yml)
- [ ] Write script to fetch workflow run history via API
- [ ] Write script to extract build duration data
- [ ] Test all scripts on one repository

---

## Phase 3: Data Collection & Baseline Analysis (March 18 - March 25)

### Week 4: March 18 - March 24

#### Day 18-19: Collect Workflow Configurations
- [ ] Download all workflow files from selected repositories
- [ ] Save in organized folder structure:
  ```
  02_data_collection/
  ├── repo1/
  │   ├── workflows/
  │   └── build_logs/
  ├── repo2/
  ...
  ```

#### Day 20-21: Collect Build History Data
- [ ] For each repository, collect last 50-100 workflow runs
- [ ] Extract and save:
  - Run ID
  - Trigger event (push, pull request, etc.)
  - Start time and end time
  - Total duration
  - Individual job durations
  - Success/failure status
- [ ] Save data in CSV format

#### Day 22-23: Analyze Current Configurations
- [ ] Review each workflow file manually
- [ ] Create inefficiency checklist for each repo:

  | Repository | Has Caching? | Parallel Jobs? | Redundant Steps? | Cache Hit Rate |
  |------------|--------------|----------------|------------------|----------------|
  | Repo 1     | Yes/No       | Yes/No         | Yes/No           | X%             |
  | Repo 2     | Yes/No       | Yes/No         | Yes/No           | X%             |
  
- [ ] Calculate baseline metrics:
  - Average build time
  - Median build time
  - Standard deviation

#### Day 24-25: Document Baseline Findings
- [ ] Create summary report of current state
- [ ] Identify specific optimization opportunities for each repo
- [ ] Plan what optimizations to apply to each repo

---

## Phase 4: Optimization Implementation & Testing (March 26 - April 10)

### Week 5: March 26 - April 1

#### Day 26-27: Fork Repositories
- [ ] Fork all selected repositories to your GitHub account
- [ ] Clone forked repos locally
- [ ] Create branches for different optimization tests:
  - `optimization/caching-only`
  - `optimization/parallel-only`
  - `optimization/combined`

#### Day 28-30: Implement Caching Optimization
- [ ] For each repository, add caching configuration:
  ```yaml
  - name: Cache dependencies
    uses: actions/cache@v4
    with:
      path: |
        ~/.npm
        # or ~/.cache/pip for Python
        # or ~/.m2 for Maven
      key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-deps-
  ```
- [ ] Commit changes to `optimization/caching-only` branch
- [ ] Push and let workflows run

#### Day 31 - April 1: Implement Parallelization Optimization
- [ ] Analyze job dependencies in each workflow
- [ ] Restructure workflows to run independent jobs in parallel
- [ ] Example before:
  ```yaml
  jobs:
    build:
      ...
    test:
      needs: build  # waits for build
    lint:
      needs: test   # waits for test
  ```
- [ ] Example after (if lint doesn't need test):
  ```yaml
  jobs:
    build:
      ...
    test:
      needs: build
    lint:
      needs: build  # runs parallel with test
  ```
- [ ] Commit to `optimization/parallel-only` branch
- [ ] Push and let workflows run

### Week 6: April 2 - April 10

#### Day 2-4: Implement Combined Optimization
- [ ] Apply both caching AND parallelization together
- [ ] Commit to `optimization/combined` branch
- [ ] Push and let workflows run

#### Day 5-7: Run Multiple Tests
- [ ] For each optimization type, trigger at least 10 workflow runs
- [ ] Methods to trigger runs:
  - Make small commits (add empty line, fix typo)
  - Use workflow_dispatch if available
  - Create pull requests
- [ ] Record all run data

#### Day 8-10: Collect Post-Optimization Data
- [ ] Gather workflow run data for all optimization branches
- [ ] Extract same metrics as baseline:
  - Total duration
  - Individual job durations
  - Cache hit/miss rates
- [ ] Save in organized CSV files:
  ```
  03_analysis/
  ├── baseline_data.csv
  ├── caching_only_data.csv
  ├── parallel_only_data.csv
  └── combined_data.csv
  ```

---

## Phase 5: Data Analysis & Visualization (April 11 - April 20)

### Week 7: April 11 - April 17

#### Day 11-12: Calculate Improvement Metrics
- [ ] For each repository and optimization type, calculate:
  - Mean build time (before vs after)
  - Median build time (before vs after)
  - Percentage reduction
  - Time saved per build
  
- [ ] Example calculation:
  ```
  Before: Average 300 seconds
  After:  Average 180 seconds
  Reduction: (300-180)/300 = 40% improvement
  ```

#### Day 13-14: Statistical Significance Testing
- [ ] Use Python scipy library for statistical tests
- [ ] Perform t-test or Mann-Whitney U test:
  ```python
  from scipy import stats
  
  # Compare before and after
  t_stat, p_value = stats.ttest_ind(before_times, after_times)
  
  # If p_value < 0.05, the difference is statistically significant
  ```
- [ ] Document results for each comparison

#### Day 15-17: Create Visualizations
- [ ] Create charts using matplotlib/seaborn:

  1. **Bar chart:** Average build time before vs after for each repo
  2. **Box plot:** Distribution of build times before vs after
  3. **Grouped bar chart:** Comparison of caching vs parallel vs combined
  4. **Line chart:** Build time trend over multiple runs
  5. **Pie chart:** Percentage of time saved by each optimization

- [ ] Save all charts as PNG files for dissertation

### Week 8: April 18 - April 20

#### Day 18-19: Summarize Findings
- [ ] Create summary tables:

  | Repository | Baseline | Caching | Parallel | Combined | Best Improvement |
  |------------|----------|---------|----------|----------|------------------|
  | Repo 1     | 300s     | 200s    | 250s     | 150s     | 50% (Combined)   |
  | Repo 2     | 450s     | 300s    | 400s     | 280s     | 38% (Combined)   |

- [ ] Identify patterns:
  - Which optimization works best overall?
  - Does project type affect results?
  - Any unexpected findings?

#### Day 20: Prepare Analysis Chapter Draft
- [ ] Write first draft of Results chapter
- [ ] Include all tables and visualizations
- [ ] Document methodology for each analysis step

---

## Phase 6: Dissertation Writing (April 21 - May 15)

### Week 9: April 21 - April 27

#### Day 21-23: Write Methodology Chapter
- [ ] Explain your research approach
- [ ] Detail each stage of methodology
- [ ] Include:
  - Repository selection criteria and process
  - Data collection methods
  - Optimization implementation details
  - Analysis techniques used
- [ ] Aim for 2000-2500 words

#### Day 24-27: Write Results Chapter
- [ ] Present all findings with supporting data
- [ ] Include all visualizations
- [ ] Structure by research question:
  - RQ1: Common inefficiencies found
  - RQ2: Impact of caching
  - RQ3: Impact of parallelization
  - RQ4: Combined effect
- [ ] Aim for 2500-3000 words

### Week 10: April 28 - May 4

#### Day 28-30: Write Discussion Chapter
- [ ] Interpret your results
- [ ] Compare with existing literature
- [ ] Discuss:
  - What do the results mean?
  - Why did certain optimizations work better?
  - Practical implications for developers
  - Limitations of your study
- [ ] Aim for 1500-2000 words

#### May 1-4: Write Introduction and Conclusion
- [ ] Introduction:
  - Background and context
  - Problem statement
  - Research questions
  - Contribution of your research
  - Dissertation structure overview
  - Aim for 1500 words

- [ ] Conclusion:
  - Summary of findings
  - Answer to research questions
  - Practical guidelines/recommendations
  - Future work suggestions
  - Aim for 1000 words

### Week 11: May 5 - May 11

#### Day 5-7: Write Abstract and Finalize Literature Review
- [ ] Write abstract (250-300 words)
- [ ] Revise and expand literature review based on your findings
- [ ] Ensure all sections flow together

#### Day 8-11: Compile Full Dissertation
- [ ] Put all chapters together in correct order:
  1. Title Page
  2. Abstract
  3. Table of Contents
  4. List of Figures/Tables
  5. Introduction
  6. Literature Review
  7. Methodology
  8. Results
  9. Discussion
  10. Conclusion
  11. References
  12. Appendices

- [ ] Format according to university guidelines
- [ ] Check all citations are correct
- [ ] Ensure all figures have captions

### Week 12: May 12 - May 15

#### Day 12-15: First Complete Review
- [ ] Read entire dissertation from start to finish
- [ ] Check for:
  - Logical flow between sections
  - Consistency in terminology
  - Grammar and spelling errors
  - Missing references
- [ ] Make necessary revisions

---

## Phase 7: Review & Submission (May 16 - May 31)

### Week 13: May 16 - May 22

#### Day 16-18: Self-Editing
- [ ] Read aloud to catch awkward sentences
- [ ] Use grammar checking tools (Grammarly, etc.)
- [ ] Verify all data and calculations are correct
- [ ] Ensure all figures are clear and readable

#### Day 19-20: Peer Review
- [ ] Ask a classmate or friend to review
- [ ] Get feedback on:
  - Clarity of writing
  - Logical flow
  - Any confusing sections

#### Day 21-22: Supervisor Feedback
- [ ] Send draft to Dr. Kazimoglu for review
- [ ] Ask for specific feedback on:
  - Methodology soundness
  - Results interpretation
  - Any missing elements

### Week 14: May 23 - May 31

#### Day 23-26: Incorporate Feedback
- [ ] Address all supervisor comments
- [ ] Make final revisions
- [ ] Double-check formatting requirements

#### Day 27-28: Final Proofreading
- [ ] One final read-through
- [ ] Check page numbers
- [ ] Verify table of contents matches actual pages
- [ ] Ensure all appendices are complete

#### Day 29-30: Prepare Submission
- [ ] Convert to required format (PDF)
- [ ] Check file size and quality
- [ ] Prepare any additional required documents

#### Day 31: Submit! 🎉
- [ ] Submit dissertation through university portal
- [ ] Keep a backup copy
- [ ] Celebrate your achievement!

---

## Quick Reference: Key Deliverables by Week

| Week | Dates | Key Deliverables |
|------|-------|------------------|
| 1 | Mar 1-7 | Ethics form submitted, Literature review draft |
| 2 | Mar 8-10 | Development environment ready, GitHub API working |
| 3 | Mar 11-17 | 5-10 repositories selected, Data collection scripts ready |
| 4 | Mar 18-25 | Baseline data collected, Inefficiencies documented |
| 5 | Mar 26 - Apr 1 | Caching and parallelization implemented |
| 6 | Apr 2-10 | All optimization tests completed, Data collected |
| 7 | Apr 11-17 | Statistical analysis done, Visualizations created |
| 8 | Apr 18-20 | Results summarized, Analysis chapter draft |
| 9 | Apr 21-27 | Methodology and Results chapters written |
| 10 | Apr 28 - May 4 | Discussion, Introduction, Conclusion written |
| 11 | May 5-11 | Full dissertation compiled and formatted |
| 12 | May 12-15 | First complete review done |
| 13 | May 16-22 | Peer review and supervisor feedback received |
| 14 | May 23-31 | Final revisions, Submission |

---

## Tools You'll Need

| Tool | Purpose |
|------|---------|
| Python 3.x | Scripts and analysis |
| pandas | Data manipulation |
| matplotlib/seaborn | Visualizations |
| scipy | Statistical tests |
| requests | GitHub API calls |
| PyYAML | Parsing workflow files |
| Git | Version control |
| VS Code | Code editing |
| Microsoft Word | Dissertation writing |
| Grammarly | Proofreading |

---

## Tips for Success

1. **Work every day** - Even 2 hours daily is better than cramming
2. **Track your progress** - Use this checklist actively
3. **Back up everything** - Use GitHub and cloud storage
4. **Ask for help early** - Don't wait until the last week
5. **Take breaks** - Burnout will slow you down
6. **Document as you go** - Don't leave all writing for the end

---

Good luck with your dissertation! You've got this! 🎓
