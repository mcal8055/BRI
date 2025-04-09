# rose_scraper.py

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# === Output directories ===
os.makedirs("screenshots/roses", exist_ok=True)

# === Dates to capture ===
dates = pd.date_range("2024-03-01", "2024-03-03").strftime("%Y-%m-%d")

# === Scrape loop ===
for date_str in dates:
    formatted_date = pd.to_datetime(date_str).strftime("%-m/%-d/%Y")
    url = f"https://utahavalanchecenter.org/forecast/salt-lake/{formatted_date}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        print(f"📸 Loading forecast for {date_str}...")
        driver.get(url)
        time.sleep(3)

        # === Locate the rose image ===
        rose_img = driver.find_element(By.CSS_SELECTOR, "img[src*='danger_rose']")
        src_url = rose_img.get_attribute("src")

        # === Download the rose image ===
        import requests
        rose_data = requests.get(src_url).content
        rose_path = f"screenshots/roses/rose_{date_str.replace('-', '')}.png"

        with open(rose_path, "wb") as f:
            f.write(rose_data)

        print(f"✅ Saved: {rose_path}")

    except Exception as e:
        print(f"❌ Error on {date_str}: {e}")
    finally:
        driver.quit()
