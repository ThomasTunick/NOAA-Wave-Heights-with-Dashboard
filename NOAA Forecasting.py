import pandas as pd
import gzip
import os

# Folder where you stored your NOAA .gz files
data_folder = "noaa_data/NOAA DATA"

# Buoy IDs and their region labels
buoy_regions = {
    "51001": "North Shore",
    "51202": "South Shore"
}

# NOAA column headers
column_names = [
    "YYYY", "MM", "DD", "hh", "mm", "WDIR", "WSPD", "GST",
    "WVHT", "DPD", "APD", "MWD", "PRES", "ATMP", "WTMP", "DEWP", "VIS", "TIDE"
]

# List to hold all dataframes
all_data = []

# Read and process each NOAA .gz file
for filename in os.listdir(data_folder):
    if filename.endswith(".gz"):
        buoy_id = filename[:5]
        if buoy_id in buoy_regions:
            region = buoy_regions[buoy_id]
            filepath = os.path.join(data_folder, filename)
            with gzip.open(filepath, 'rt') as f:
                print(f"Reading {filename}...")
                df = pd.read_csv(
                    f,
                    sep='\\s+',
                    skiprows=1,
                    names=column_names,
                    na_values=['MM', '999.0', '99.00', '9999.0'],
                    engine='python'
                )
                # Create datetime column safely
                df["datetime"] = pd.to_datetime(
                    df[["YYYY", "MM", "DD", "hh"]].astype(str).agg('-'.join, axis=1),
                    format='%Y-%m-%d-%H',
                    errors='coerce'
                )
                df["region"] = region
                df["buoy"] = buoy_id
                all_data.append(df)

# Combine all into one DataFrame
combined = pd.concat(all_data, ignore_index=True)

# Drop rows with bad datetimes or missing wave height
combined = combined.dropna(subset=["datetime", "WVHT"])

# Sort by time just in case
combined = combined.sort_values("datetime")

# Convert WVHT to float and clean up any non-numeric rows
combined["WVHT"] = pd.to_numeric(combined["WVHT"], errors="coerce")
combined = combined.dropna(subset=["WVHT"])

# Add a column with just the date part (YYYY-MM-DD)
combined["date"] = combined["datetime"].dt.date

# Group by region and date, and compute average wave height
daily_avg = combined.groupby(["region", "date"])["WVHT"].mean().reset_index()

# Rename column for clarity
daily_avg = daily_avg.rename(columns={"WVHT": "avg_wave_height"})


import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

# Separate lines per region
for region in daily_avg["region"].unique():
    region_data = daily_avg[daily_avg["region"] == region]
    plt.plot(region_data["date"], region_data["avg_wave_height"], label=region, marker='o')

plt.title("Average Daily Wave Height by Region")
plt.xlabel("Date")
plt.ylabel("Wave Height (meters)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Preview result
print(combined.head())
print("Total rows:", len(combined))
print("Regions included:", combined['region'].unique())

# Save the daily average data for Streamlit
daily_avg.to_csv("daily_avg.csv", index=False)
print("✅ Saved: daily_avg.csv")
