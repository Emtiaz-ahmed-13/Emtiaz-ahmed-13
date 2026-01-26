import requests
from datetime import datetime, timedelta
import re

# =========================
# USER CONFIG
# =========================
GITHUB_USERNAME = "Emtiaz-ahmed-13"
LEETCODE_USERNAME = "emtiaz"
CODEFORCES_USERNAME = "Prince_Emtiaz"
README_FILE = "README.md"


# =========================
# GITHUB STREAK (COSMETIC)
# =========================
def get_github_contributions():
    """
    NOTE:
    This is a cosmetic streak based on a fixed start date.
    For real contribution streak, GitHub GraphQL + token is required.
    """
    start_date = datetime(2025, 12, 31)
    today = datetime.utcnow()
    days = (today - start_date).days + 1

    return (
        days,
        start_date.strftime("%b %d, %Y"),
        today.strftime("%b %d, %Y")
    )


def update_readme_github_streak(days, start_date, end_date):
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update Badge Count
    # Looks for badge/GitHub-27_Days
    content = re.sub(
        r"badge/GitHub-\d+_Days",
        f"badge/GitHub-{days}_Days",
        content
    )

    # Update Date Range
    # Looks for <!--GITHUB_DATE_START-->...<!--GITHUB_DATE_END-->
    content = re.sub(
        r"<!--GITHUB_DATE_START-->.*?<!--GITHUB_DATE_END-->",
        f"<!--GITHUB_DATE_START-->{start_date} → {end_date}<!--GITHUB_DATE_END-->",
        content
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ GitHub streak updated: {days} days")


# =========================
# LEETCODE STREAK
# =========================
# =========================
# LEETCODE STREAK
# =========================
def get_leetcode_streak(username):
    try:
        url = f"https://leetcode-stats-api.herokuapp.com/{username}"
        data = requests.get(url, timeout=10).json()

        # Check for API-provided streak first (though sometimes inaccurate)
        # if "streak" in data and data["streak"] > 0:
        #     return data["streak"]
        
        # Fallback: Calculate manually from submissionCalendar
        calendar = data.get("submissionCalendar", {})
        if not calendar:
            return 0
            
        # Parse timestamps to dates
        solved_days = set()
        for ts_str in calendar.keys():
            # timestamps are in seconds
            ts = int(ts_str)
            date = datetime.utcfromtimestamp(ts).date()
            solved_days.add(date)

        # -----------------------------------------------
        # MANUAL FIX: Time Travel Tickets / Streak Freezes
        # Add dates here that you repaired on LeetCode
        # -----------------------------------------------
        MANUAL_FILL_DATES = [
            "2025-07-17",  # Fixed gap
            "2025-07-11",  # Fixed gap 2
        ]
        
        for date_str in MANUAL_FILL_DATES:
            try:
                manual_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                solved_days.add(manual_date)
            except ValueError:
                pass
        # -----------------------------------------------
            
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Determine start date for streak check
        if today in solved_days:
            current = today
        elif yesterday in solved_days:
            current = yesterday
        else:
            return 0
            
        streak = 0
        while current in solved_days:
            streak += 1
            current -= timedelta(days=1)
            
        return streak

    except Exception as e:
        print(f"⚠️ LeetCode Error: {e}")
        return "N/A"


# =========================
# CODEFORCES STREAK
# =========================
def get_codeforces_streak(username):
    try:
        url = f"https://codeforces.com/api/user.status?handle={username}"
        data = requests.get(url, timeout=10).json()

        if data["status"] != "OK":
            return "N/A"

        solved_days = set()
        for sub in data["result"]:
            day = datetime.utcfromtimestamp(sub["creationTimeSeconds"]).date()
            solved_days.add(day)

        streak = 0
        today = datetime.utcnow().date()

        while today in solved_days:
            streak += 1
            today -= timedelta(days=1)

        return streak
    except Exception:
        return "N/A"


# =========================
# UPDATE README CP STREAKS
# =========================
def update_readme_cp_streaks(leetcode, codeforces):
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # LeetCode Badge
    content = re.sub(
        r"badge/LeetCode-\d+_Days",
        f"badge/LeetCode-{leetcode}_Days",
        content
    )

    # Codeforces Badge
    content = re.sub(
        r"badge/Codeforces-\d+_Days",
        f"badge/Codeforces-{codeforces}_Days",
        content
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Competitive programming streaks updated")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🔄 Updating GitHub profile streaks...\n")

    # GitHub streak
    days, start, end = get_github_contributions()
    update_readme_github_streak(days, start, end)

    # CP streaks
    leetcode_streak = get_leetcode_streak(LEETCODE_USERNAME)
    codeforces_streak = get_codeforces_streak(CODEFORCES_USERNAME)

    update_readme_cp_streaks(leetcode_streak, codeforces_streak)

    print("\n✅ All streaks updated successfully!")
