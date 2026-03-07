# Meeting Agenda - Dissertation Proposal Discussion

**Student:** Sagar Gurung (33147045)  
**Supervisor:** Dr. Cain Kazimoglu  
**Date:** 27th feb Wednesday (in Person)

---

## 1. Why I Do Not Want to Continue with the Previous Proposal

**Previous Topic:** "Reducing the Impact of Flaky Tests in GitHub Actions CI/CD Pipelines"

**Reasons for changing:**

- The methodology was not clear enough to execute properly
- Missing foundational techniques like CI mining and threshold-based analysis
- The scope was too broad and difficult to measure
- Flaky test detection seems it requires complex analysis that may not be achievable in the given timeline

---

## 2. Research for what?

- For the measurable impact of applying caching and parallelization optimization strategies on build times in GitHub Actions workflows
- For the common build time inefficiencies in GitHub Actions workflows of open-source projects

## 3. What is the New Proposal About

**New Topic:** "An Empirical Analysis of Build Time Optimization Strategies in GitHub Actions"

**Key Points:**

- Focus on two specific optimization techniques: Caching and Parallelization
- Analyze 5-10 real open-source GitHub repositories
- Measure actual build time improvements with numbers

---

## 4. Methodology in short

### Stage 1: Repository Selection

- Find 5-10 open-source projects on GitHub that use GitHub Actions
- Selection criteria: at least 100 stars, at least 50 workflow runs, common programming languages (JavaScript, Python, Java)
- Use GitHub API to search and filter projects

### Stage 2: Data Collection

- Download workflow files (.yml) from each project
- Collect build logs showing how long builds take
- Record cache usage and job structure
- Store everything in organized files (JSON/CSV)

### Stage 3: Inefficiency Identification

- Look at each project's workflow configuration
- Find problems like:
  - No caching set up for dependencies
  - Jobs running one after another when they could run together
  - Same dependencies being downloaded multiple times
- Use thresholds (e.g., cache hit rate below 50% = inefficient)

### Stage 4: Optimization Implementation

- Create copies (forks) of selected projects
- Add caching using GitHub's actions/cache feature
- Restructure jobs to run in parallel where possible
- Test both separately and together

### Stage 5: Measurement and Analysis

- Run workflows multiple times (at least 10 runs each)
- Measure build time before and after optimization
- Calculate percentage improvement
- Use statistical tests to confirm results are significant
- Create charts and graphs to show findings

### Stage 6: Guidelines Development

- Based on results, write practical recommendations
- Create templates developers can use
- Make a checklist for identifying optimization opportunities

---

## 5. QA

- Is the scope of 5-10 repositories appropriate?
- Is the March-May 2026 timeline realistic? (extension how many days i get?)
- Any suggestions for repository selection criteria?
- Are there any additional optimization techniques I should consider?
- Any recommended tools or resources for data collection?

---
