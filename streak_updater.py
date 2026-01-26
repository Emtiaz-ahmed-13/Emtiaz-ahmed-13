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

    # Update Days
    # Looks for <!--GITHUB_START-->20<!--GITHUB_END-->
    content = re.sub(
        r"<!--GITHUB_START-->.*?<!--GITHUB_END-->",
        f"<!--GITHUB_START-->{days}<!--GITHUB_END-->",
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
def get_leetcode_streak(username):
    try:
        url = f"https://leetcode-stats-api.herokuapp.com/{username}"
        data = requests.get(url, timeout=10).json()
        return data.get("streak", "N/A")
    except Exception:
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

    # LeetCode
    content = re.sub(
        r"<!--LEETCODE_START-->.*?<!--LEETCODE_END-->",
        f"<!--LEETCODE_START-->{leetcode}<!--LEETCODE_END-->",
        content
    )

    # Codeforces
    content = re.sub(
        r"<!--CODEFORCES_START-->.*?<!--CODEFORCES_END-->",
        f"<!--CODEFORCES_START-->{codeforces}<!--CODEFORCES_END-->",
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
