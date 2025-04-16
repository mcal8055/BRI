import os
import re
import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# === Canonical avalanche problem types (for modeling output) ===
canonical_problems = [
    "New Snow", "Wind-Drifted Snow", "Persistent Weak Layer",
    "Wet Snow", "Gliding Snow", "Cornices"
]

# === Aliases used in actual UAC forecasts (mapped to canonical labels) ===
problem_aliases = {
    # New Snow
    "Storm Slab": "New Snow",
    "Loose Dry": "New Snow",
    "Dry Loose": "New Snow",

    # Wind-Drifted Snow
    "Wind Slab": "Wind-Drifted Snow",
    "Wind Drifted Snow": "Wind-Drifted Snow",

    # Persistent Weak Layer
    "Persistent Slab": "Persistent Weak Layer",

    # Wet Snow
    "Wet Slab": "Wet Snow",
    "Loose Wet": "Wet Snow",
    "Wet Loose": "Wet Snow",

    # Gliding Snow
    "Glide Avalanche": "Gliding Snow",

    # Cornices
    "Cornice Fall": "Cornices",
    "Cornices": "Cornices"
}

# === Dates to test ===
date_range = pd.date_range(start='2024-11-24', end='2025-04-09')


problem_rows = []

# === Scraping loop ===
for date_str in date_range:
    print(f"\n📆 Scraping forecast for {date_str}...")

    formatted_date = pd.to_datetime(date_str).strftime("%-m/%-d/%Y")
    url = f"https://utahavalanchecenter.org/forecast/salt-lake/{formatted_date}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, scroll_height)

        # Grab all strong tags
        strong_tags = driver.find_elements(By.TAG_NAME, "strong")

        # Define the possible danger levels
        danger_levels = ["LOW", "MODERATE", "CONSIDERABLE", "HIGH", "EXTREME"]

        # Loop through the strong tags and find the first one that matches a danger level
        danger_rating = None
        for tag in strong_tags:
            if tag.text.upper() in danger_levels:
                danger_rating = tag.text.upper()
                break

        # If no danger rating was found, set it to None
        if not danger_rating:
            danger_rating = "None"

        # Grab visible forecast text from body
        text = driver.find_element(By.TAG_NAME, "body").text
        driver.quit()

        # === Extract problem titles that follow "Avalanche Problem #X" ===
        problem_titles = re.findall(
            r"Avalanche Problem\s*#?\d+\s*\n(.*?)\n", text, re.IGNORECASE
        )

        # === Normalize using aliases ===
        problems_found = []
        for raw_title in problem_titles:
            title_clean = raw_title.strip()
            normalized = problem_aliases.get(title_clean, title_clean)

            if normalized not in problems_found:
                problems_found.append(normalized)

        print(f"✔️ Problems found for {date_str}: {problems_found}")
        print(f"✔️ Danger Rating for {date_str}: {danger_rating}")

        # === Store rows ===
        for i, problem in enumerate(problems_found):
            problem_rows.append({
                "forecast_id": "f" + pd.to_datetime(date_str).strftime("%Y%m%d"),
                "date": date_str,
                "problem_number": i + 1,
                "problem_type": problem,
                "danger_rating": danger_rating,
                "danger_low": "TBD",
                "danger_mid": "TBD",
                "danger_high": "TBD",
                "likelihood": "TBD",
                "size": "TBD"
            })


    except Exception as e:
        print(f"❌ Failed to process {date_str}: {e}")
        driver.quit()

# === Output to DataFrame ===
df_problems = pd.DataFrame(problem_rows)

# === Pivot avalanche problems into structured columns ===
pivoted = df_problems.pivot(index="forecast_id", columns="problem_number", values="problem_type").reset_index()
pivoted.columns.name = None

# Rename up to 5 Avalanche Problem columns
pivoted = pivoted.rename(columns={
    1: "Avalanche Problem #1",
    2: "Avalanche Problem #2",
    3: "Avalanche Problem #3",
    4: "Avalanche Problem #4",
    5: "Avalanche Problem #5"
})

# Fill missing problem columns (if fewer than 5)
for i in range(1, 6):
    col = f"Avalanche Problem #{i}"
    if col not in pivoted.columns:
        pivoted[col] = np.nan

# Reattach the date
forecast_dates = df_problems.drop_duplicates("forecast_id")[["forecast_id", "date"]]
pivoted = forecast_dates.merge(pivoted, on="forecast_id")

# Add placeholders for upcoming fields
pivoted["danger_low"] = "TBD"
pivoted["danger_mid"] = "TBD"
pivoted["danger_high"] = "TBD"
pivoted["likelihood"] = "TBD"
pivoted["size"] = "TBD"

# Display final structured table
print("\n📊 Forecast Table (Structured):")
print(pivoted.to_string(index=False))

# === Save to CSV ===
os.makedirs('data', exist_ok=True)
pivoted.to_csv('data/forecast_data.csv', index=False)
print("✅ Data saved to 'data/forecast_data.csv'")
