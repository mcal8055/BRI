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
test_dates = ["2025-03-01", "2025-03-17", "2025-03-03"]

# === Where we store the result ===
problem_rows = []

# === Scraping loop ===
for date_str in test_dates:
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

        # === Store rows ===
        for i, problem in enumerate(problems_found):
            problem_rows.append({
                "forecast_id": "f" + pd.to_datetime(date_str).strftime("%Y%m%d"),
                "date": date_str,
                "problem_number": i + 1,
                "problem_type": problem,
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


# -----------------------------
# TEMPLATE MATCHING (for later)
# -----------------------------
"""
# ===============================
# TEMPLATE MATCHING: Likelihood Detection
# ===============================
# This block uses OpenCV to dynamically locate the Likelihood graphic
# in the full forecast screenshot using a template image.

import cv2
import numpy as np

# Load full screenshot and the template image
full_img = cv2.imread("forecast_screenshot.png")
template = cv2.imread("likelihood_template.png")

# Convert to grayscale
full_gray = cv2.cvtColor(full_img, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# Template matching
res = cv2.matchTemplate(full_gray, template_gray, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

# Coordinates of matched region
top_left = max_loc
h, w = template.shape[:2]
bottom_right = (top_left[0] + w, top_left[1] + h)

# Crop matched region
matched_crop = full_img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
cv2.imwrite("matched_likelihood_block.png", matched_crop)

# Divide the matched block into 5 rows and find the row with the blue arrow
likelihood_scale = {
    1: "Certain",
    2: "Very Likely",
    3: "Likely",
    4: "Possible",
    5: "Unlikely"
}

arrow_row = None
row_height = h // 5
for i in range(5):
    row = matched_crop[i * row_height:(i + 1) * row_height, :]
    blue_pixels = 0
    for y in range(row.shape[0]):
        for x in range(row.shape[1]):
            b, g, r = row[y, x]
            if r < 100 and g < 100 and b > 150:
                blue_pixels += 1
    if blue_pixels > 20:
        arrow_row = i + 1
        break

likelihood_result = likelihood_scale.get(arrow_row, "Unknown")

print("📍 Detected Likelihood via Template Match:", likelihood_result)
"""
