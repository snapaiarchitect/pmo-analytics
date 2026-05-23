import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load FTA NTD Capital Expenses data
# Source: Federal Transit Administration National Transit Database
# API: https://data.transportation.gov/resource/fphd-jyyj.csv
print("Loading FTA NTD Capital Expenses data...")
df = pd.read_csv('https://data.transportation.gov/resource/fphd-jyyj.csv?$limit=50000')

print(f"Records loaded: {len(df):,}")
print(f"Year range: {df.report_year.min()} - {df.report_year.max()}")
print(f"Unique agencies: {df.agency.nunique():,}")
print(f"Unique transit modes: {df.mode_name.nunique()}")
print(f"Data source: FTA National Transit Database (NTD)")
print(f"API endpoint: https://data.transportation.gov/resource/fphd-jyyj.csv")
print(f"Last accessed: 2025-05-18")

df.head()
