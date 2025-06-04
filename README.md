# YouTube Subscription Importer

Automate re-subscribing to your favorite YouTube channels on a new account using data exported via [Google Takeout](https://takeout.google.com/). This script uses Selenium to log in and re-subscribe to each channel.

---

## 📦 Features

- ✅ Imports channels from `subscriptions.csv`
- ✅ Logs all successful subscriptions
- ✅ Skips and logs channels that fail
- ✅ Can resume where it left off after interruption
- ✅ Restarts browser every 25 subscriptions for stability

---

## 🐧 Compatibility

🧪 **Tested on Linux only**  
May work on Windows/macOS with minor adjustments, but not guaranteed.

---

## 🔧 Requirements

- Python 3.7+
- Google Chrome
- ChromeDriver (same version as your Chrome)

---

## 📥 How to Use

### 1. Export from Google Takeout

1. Go to [Google Takeout](https://takeout.google.com/).
2. Select only **YouTube and YouTube Music**.
3. Export format: `.zip`, then extract it.
4. Inside `subscriptions/` you’ll find a file like `subscriptions.csv`.

Copy this CSV to the same folder as the script.

---

### 2. Install Python Requirements

```bash
pip install -r requirements.txt
```

---

### 3. Download ChromeDriver

Download the version matching your installed Chrome:
👉 https://chromedriver.chromium.org/downloads

Unzip and place it in your system `PATH` or next to the script.

---

### 4. Run the Script

```bash
python3 youtube_resubscribe.py
```

The browser will open. Login to your new YouTube account, press Enter, and it will begin.

---

## 📁 Output Files

- `subscription_log.txt` – Successful subscriptions
- `skipped_channels.csv` – Any failures, for retry later
- `last_offset.txt` – Stores the resume point if interrupted

---

## 🛑 Notes

- This script mimics human behavior but **may still hit rate limits** if used excessively.
- Use responsibly. Do not spam or violate YouTube’s Terms of Service.

---

## 🛠 Troubleshooting

- **Profile locked?**
  ```bash
  pkill -f "chrome.*selenium-profile"
  ```
- **ChromeDriver mismatch?** Ensure Chrome and ChromeDriver versions match exactly.

---

## 🧪 Tested On

- openSUSE Tumbleweed
- Google Chrome 123+
- Selenium 4.14.0
