# YouTube Subscription Importer

Automate re-subscribing to your favorite YouTube channels on a new account using data exported via [Google Takeout](https://takeout.google.com/). This script uses **undetected-chromedriver** to bypass bot detection, handles login sessions intelligently, and includes a robust retry mechanism.

---

## 📦 Features

- ✅ **Headless Mode**: Runs silently in the background (default).
- ✅ **Smart Session**: Saves cookies (`cookies.pkl`) so you only log in once.
- ✅ **Auto-Retry**: Automatically retries failed subscriptions at the end.
- ✅ **Resumable**: Can resume where it left off after interruption.
- ✅ **Stability**: Restarts browser every 20 subscriptions to prevent memory leaks/hangs.

---

## 🐧 Compatibility

- 🧪 **Tested on Linux and MacOS**
- Should work on Windows with minor path adjustments.

---

## 🔧 Requirements

- Python 3.13+
- Google Chrome installed

The script handles the ChromeDriver execution automatically using `undetected-chromedriver`.

> **Note:** Python 3.12+ dropped `distutils` from the standard library, which `undetected-chromedriver` still relies on. `requirements.txt` includes `setuptools` (which provides a `distutils` shim) to cover this — just make sure you install requirements with `python3 -m pip install -r requirements.txt` inside your venv (not a `pip` that's aliased elsewhere, e.g. to `pipx`).

---

## 📥 How to Use

### 1. Export from Google Takeout

1. Go to [Google Takeout](https://takeout.google.com/).
2. Select only **YouTube and YouTube Music**.
3. Export format: `.zip`, then extract it.
4. Finds `subscriptions.csv` inside `subscriptions/`.

Copy `subscriptions.csv` to the same folder as the script.

---

### 2. Install Python Requirements

```bash
pip install -r requirements.txt
```

---

### 3. Run the Script

```bash
python3 youtube_resubscribe.py
```

**First Run:**
- The browser will open (visible) for you to log in to your Google Account.
- Once logged in, press **Enter** in the terminal.
- The script will save your session and switch to headless mode (optional in code) or continue processing.

**Subsequent Runs:**
- It uses the saved session (`cookies.pkl`) and runs immediately.

---

## 📁 Output Files

- `subscription_log.txt` – Successful subscriptions.
- `skipped.csv` – Temporarily stores skipped channels during the run.
- `problem.csv` – Channels that failed even after retrying (Likely terminated channels or 404s).
- `last_offset.txt` – Stores the resume point.

---

## 🛑 Notes

- This script mimics human behavior but **may still hit rate limits**.
- Use responsibly. Do not spam or violate YouTube’s Terms of Service.

---

## 🛠 Troubleshooting

- **Profile locked?**
  ```bash
  pkill -f "chrome.*selenium"
  ```
- **Login issues?** Delete `cookies.pkl` and run the script again to re-login.

---

## 🧪 Tested On

- openSUSE Tumbleweed
- MacOS Sequoia
- Python 3.11+
