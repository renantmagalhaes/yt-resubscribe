import csv
import re
import time
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc

# === Config ===
csv_file = "subscriptions.csv"
log_file = "subscription_log.txt"
skipped_file = "skipped_channels.csv"
problem_file = "channels_with_problem.csv"
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
def get_chrome_options():
    options = uc.ChromeOptions()
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-data-dir=selenium-profile")
    return options

def get_chrome_major_version():
    for binary in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        try:
            output = subprocess.check_output([binary, "--version"], text=True)
            match = re.search(r"(\d+)\.", output)
            if match:
                return int(match.group(1))
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return None

chrome_major_version = get_chrome_major_version()

# Check if profile exists; if not, run headful for login
if not os.path.exists("selenium-profile"):
    print("⚠️  No session found. Launching browser for MANUAL login...")
    driver = uc.Chrome(options=get_chrome_options(), headless=False, version_main=chrome_major_version)
    driver.get("https://www.youtube.com")
    input("👉 Log into your YouTube account in the opened browser, then press Enter here to continue...")
    driver.quit()
    print("✅ Login session saved.")

print("🚀 Running in HEADLESS mode using saved session...")
driver = uc.Chrome(options=get_chrome_options(), headless=True, version_main=chrome_major_version)

# === Helper Function ===
def subscribe_to_channel(driver, channel_url, channel_title):
    try:
        driver.get(channel_url)
    except Exception as e:
        print(f"❌ Failed to load page for {channel_title}: {e}")
        return "Load Error"

    try:
        wait = WebDriverWait(driver, 10)
        subscribe_button = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//button[.//div[text()='Subscribe'] or text()='Subscribe']"
        )))
        driver.execute_script("arguments[0].click();", subscribe_button)
        print(f"✅ Subscribed to {channel_title}")
        return "Success"

    except TimeoutException:
        print(f"❌ Timeout — Subscribe button not found for: {channel_title}")
        return "Subscribe button not found"
    except Exception as e:
        print(f"❌ Error subscribing to {channel_title}: {e}")
        return str(e)

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

        result = subscribe_to_channel(driver, channel_url, channel_title)
        
        if result == "Success":
            log.write(f"Subscribed: {channel_title} ({channel_url})\n")
            log.flush()
        else:
            skipped_writer.writerow([channel_title, channel_url, result])
            skipped.flush()

        # Save offset
        with open(offset_file, "w") as ofs:
            ofs.write(str(index + 1))

        # Throttle
        time.sleep(1.5)

        # Restart browser every 25 subs
        if (index + 1) % 25 == 0:
            print("🔄 Restarting browser to avoid memory/timeouts...")
            driver.quit()
            driver = uc.Chrome(options=get_chrome_options(), headless=True, version_main=chrome_major_version)

skipped.close()

# === Retry Skipped Channels ===
# === Retry Skipped Channels ===
if os.path.exists(skipped_file) and os.path.getsize(skipped_file) > 0:
    print("\n⚠️ Retrying skipped channels...")
    
    # Read all skipped channels into memory first
    with open(skipped_file, "r", encoding="utf-8") as f:
        all_skipped = list(csv.reader(f))
    
    total_skipped = len(all_skipped)
    print(f"Found {total_skipped} channels to retry.")

    # We will process them one by one.
    # After each one, we:
    # 1. Update problems file if needed
    # 2. Rewrite the skipped file with REMAINING items (so processed ones are gone)
    
    problem_fh = open(problem_file, "a", newline="", encoding="utf-8")
    problem_writer = csv.writer(problem_fh)

    # Copy list to iterate
    remaining_skipped = all_skipped[:]

    for i in range(total_skipped):
        row = all_skipped[i]
        if not row: continue
        
        channel_title = row[0]
        channel_url = row[1]
        
        print(f"[{i+1}/{total_skipped}] Retrying: {channel_title}...")
        result = subscribe_to_channel(driver, channel_url, channel_title)
        
        if result == "Success":
            log.write(f"Subscribed (Retry): {channel_title} ({channel_url})\n")
            log.flush()
        else:
            # Failed again -> Move to problem file immediately
            print(f"❌ Failed again. Moving to {problem_file}")
            problem_writer.writerow([channel_title, channel_url, result])
            problem_fh.flush()

        # Remove current item from remaining list
        # We know we are processing index 'i', so we want everything after 'i'
        # Actually safer to just pop(0) if we are iterating consistently, 
        # but let's just slice: remaining is everything from i+1 onwards
        remaining_to_write = all_skipped[i+1:]
        
        # Rewrite skipped file immediately with ONLY the remaining items
        with open(skipped_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(remaining_to_write)
            f.flush()
        
        time.sleep(1.5)

    problem_fh.close()
    print("🎉 Retry complete!")
else:
    print("\n✅ No skipped channels to retry.")

driver.quit()
log.close()
print("\n🎉 Done! All channels processed.")
