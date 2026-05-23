# Data Sources

## Primary Data Sources

| Source | Type | Description | URL |
|--------|------|-------------|-----|
| U.S. Census ACS API | Government API | American Community Survey for executive demographic baselines | https://api.census.gov/ |
| BLS Public Data API | Government API | Employment and wage statistics for workforce analysis | https://www.bls.gov/developers/ |
| DC Open Data | Government Portal | District metrics for local executive dashboards | https://opendata.dc.gov/ |

## Data Provenance

- Census ACS 5-Year Estimates for demographic profiling
- BLS monthly employment series for labor market tracking
- DC performance metrics for municipal benchmarking

## Data Files

No local CSV — data fetched on-demand via API.

## Refresh Strategy

- Census ACS updates annually
- BLS releases monthly
- Re-fetch via APIs for latest data
