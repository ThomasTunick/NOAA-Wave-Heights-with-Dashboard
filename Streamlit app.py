import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Load cleaned data
@st.cache_data
def load_data():
    return pd.read_csv("daily_avg.csv", parse_dates=["date"])


daily_avg = load_data()

# App Title
st.title("NOAA Wave Height Dashboard")
st.markdown("Visualize average wave heights by region using NOAA buoy data.")

# Aggregation selector
aggregation = st.radio("Choose aggregation:", ["Daily", "Weekly", "Monthly"])

# Apply resampling for Weekly / Monthly
df = daily_avg.copy()
if aggregation == "Weekly":
    df = (
        df.set_index("date")
        .groupby("region")["avg_wave_height"]
        .resample("W")
        .mean()
        .dropna()
        .reset_index()
    )
elif aggregation == "Monthly":
    df = (
        df.set_index("date")
        .groupby("region")["avg_wave_height"]
        .resample("M")
        .mean()
        .dropna()
        .reset_index()
    )

# Plot each region
regions = df["region"].unique()
for region in regions:
    region_data = df[df["region"] == region]

    st.subheader(f" {region} – {aggregation} Average Wave Height")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(region_data["date"], region_data["avg_wave_height"], marker='o', label=region)
    ax.set_xlabel("Date")
    ax.set_ylabel("Avg Wave Height (m)")
    ax.set_title(f"{region} – {aggregation} Wave Height")
    ax.grid(True)
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis to prevent overlap
    st.pyplot(fig)

# Optional raw data
if st.checkbox("Show raw data table"):
    st.dataframe(df)

# Monthly summary stats
if aggregation == "Monthly":
    st.subheader(" Monthly Summary – Highest and Lowest by Region")

    stats = (
        df.groupby("region")
        .apply(lambda g: pd.Series({
            "max_value": g["avg_wave_height"].max(),
            "max_date": g.loc[g["avg_wave_height"].idxmax(), "date"],
            "min_value": g["avg_wave_height"].min(),
            "min_date": g.loc[g["avg_wave_height"].idxmin(), "date"],
        }))
        .reset_index()
    )

    for _, row in stats.iterrows():
        st.markdown(
            f"**{row['region']}**  "
            f"Highest: {row['max_value']:.2f} m in {row['max_date'].strftime('%B %Y')} | "
            f"Lowest: {row['min_value']:.2f} m in {row['min_date'].strftime('%B %Y')}"
        )
