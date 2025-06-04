import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

# === Config ===
csv_file = "subscriptions.csv"
log_file = "subscription_log.txt"
skipped_file = "skipped_channels.csv"
offset_file = "last_offset.txt"

# === Load resume point if available ===
start_index = 0
if os.path.exists(offset_file):
    with open(offset_file, 'r') as f:
        try:
            start_index = int(f.read().strip())
        except ValueError:
            pass

# === Setup Chrome ===
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=selenium-profile")
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# === Login manually ===
driver.get("https://www.youtube.com")
input("👉 Log into your NEW YouTube account in the opened browser, then press Enter here to continue...")

# === Prepare logs and skipped file ===
log = open(log_file, "a", encoding="utf-8")
skipped = open(skipped_file, "a", newline="", encoding="utf-8")
skipped_writer = csv.writer(skipped)

# === Load CSV and start subscribing ===
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = list(csv.DictReader(f))
    total = len(reader)

    for index, row in enumerate(reader[start_index:], start=start_index):
        channel_url = row["Channel URL"]
        channel_title = row["Channel title"]
        print(f"\n[{index+1}/{total}] 🌐 {channel_title} ({channel_url})")

        try:
            driver.get(channel_url)
        except Exception as e:
            print(f"❌ Failed to load page for {channel_title}: {e}")
            skipped_writer.writerow([channel_title, channel_url, "Load Error"])
            continue

        try:
            wait = WebDriverWait(driver, 6)
            subscribe_button = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//button[.//div[text()='Subscribe'] or text()='Subscribe']"
            )))
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", subscribe_button)
            time.sleep(0.5)
            subscribe_button.click()
            print(f"✅ Subscribed to {channel_title}")
            log.write(f"Subscribed: {channel_title} ({channel_url})\n")

        except TimeoutException:
            print(
                f"❌ Timeout — Subscribe button not found for: {channel_title}")
            skipped_writer.writerow(
                [channel_title, channel_url, "Subscribe button not found"])
        except Exception as e:
            print(f"❌ Error subscribing to {channel_title}: {e}")
            skipped_writer.writerow([channel_title, channel_url, str(e)])

        # Save offset
        with open(offset_file, "w") as ofs:
            ofs.write(str(index + 1))

        # Throttle
        time.sleep(1.5)

        # Restart browser every 25 subs
        if (index + 1) % 25 == 0:
            print("🔄 Restarting browser to avoid memory/timeouts...")
            driver.quit()
            driver = webdriver.Chrome(service=service, options=chrome_options)

driver.quit()
log.close()
skipped.close()
print("\n🎉 Done! All channels processed.")
