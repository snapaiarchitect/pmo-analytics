## Project 2: Multi-Workstream Program Tracker

**Context:** Program management office (PMO) tool inspired by WMATA's multi-workstream delivery across engineering, finance, operations, and executive leadership.

**Dataset:**
- Simulated multi-workstream program data
- [OpenProject API data](https://www.openproject.org/)
- [Monday.com API exports](https://monday.com/)

**Objective:** Create a unified program tracker that maps dependencies, resources, and milestones across 4–6 parallel workstreams, enabling proactive risk management and resource reallocation.

**Techniques:**
- NetworkX dependency graph analysis
- Resource leveling and critical path method (CPM)
- Risk heatmapping with Monte Carlo simulation
- Automated status rollup and escalation triggers

**Business Impact:**
- Proactive identification of schedule risks before they become delays
- Resource reallocation recommendations based on workload analysis
- Standardized milestone tracking across 12+ stakeholders
- Reduced manual status reporting effort by 60%

**Files:**
- `notebooks/01_dependency_mapping.ipynb`
- `notebooks/02_resource_leveling.ipynb`
- `notebooks/03_monte_carlo_risk.ipynb`
- `src/dependency_graph.py`
- `src/resource_optimizer.py`
- `src/status_rollup.py`
- `dashboard/program_tracker.py`

**Status:** 🔧 In development
