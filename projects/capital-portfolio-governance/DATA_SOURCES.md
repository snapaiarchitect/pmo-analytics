# Data Sources

## Primary Data Sources

| Source | Type | Description | URL |
|--------|------|-------------|-----|
| USASpending.gov | Government API | Federal awards, contracts, grants by agency | https://www.usaspending.gov/ |
| FTA NTD | Government Database | National Transit Database — capital spending | https://www.transit.dot.gov/ntd | 
| WMATA Capital Program | Transit Agency | WMATA capital improvement projects | https://www.wmata.com/about/records/foia/ |

## Data Provenance

- USASpending API: Federal contract obligations by agency and program
- FTA NTD: Annual capital expenditure reporting from transit agencies
- WMATA: FOIA-disclosed capital program documents

## Data Files

No local CSV — data fetched on-demand via API or downloaded from public sources.

## Refresh Strategy

- USASpending updates daily
- FTA NTD publishes annually
- Re-fetch via API for latest federal spending data
