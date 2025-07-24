import requests # type: ignore
from datetime import datetime

LEETCODE_USERNAME = "emtiaz"
CODEFORCES_USERNAME = "Prince_Emtiaz"

def get_leetcode_streak(username):
    try:
        url = f"https://leetcode-stats-api.herokuapp.com/{username}"
        response = requests.get(url)
        data = response.json()
        streak = data.get("streak", "N/A")
        return f"- 🔹 LeetCode Daily Streak: `{streak} days`"
    except:
        return "- 🔹 LeetCode Daily Streak: `Error fetching streak`"

def get_codeforces_contest_streak(username):
    try:
        url = f"https://codeforces.com/api/user.rating?handle={username}"
        response = requests.get(url)
        data = response.json()

        if data["status"] != "OK":
            return "- 🔹 Codeforces Contest Streak: `Error fetching data`"

        contests = data["result"]
        if not contests:
            return "- 🔹 Codeforces Contest Streak: `0 contests`"

        streak = 1
        for i in range(len(contests) - 1, 0, -1):
            prev = datetime.utcfromtimestamp(contests[i - 1]["ratingUpdateTimeSeconds"])
            curr = datetime.utcfromtimestamp(contests[i]["ratingUpdateTimeSeconds"])
            if (curr - prev).days <= 10:
                streak += 1
            else:
                break

        return f"- 🔹 Codeforces Contest Streak: `{streak} contests in a row`"
    except:
        return "- 🔹 Codeforces Contest Streak: `Error fetching streak`"

def update_readme(streak_lines):
    with open("README.md", "r", encoding="utf-8") as f:
        lines = f.readlines()

    start = None
    for i, line in enumerate(lines):
        if "### 🔥 Streaks (Updated Automatically)" in line:
            start = i
            break

    if start is not None:
        lines = lines[:start + 1]
        lines.append("\n")
        lines.extend(streak_lines)
        lines.append("\n")

        with open("README.md", "w", encoding="utf-8") as f:
            f.writelines(lines)

if __name__ == "__main__":
    leetcode_line = get_leetcode_streak(LEETCODE_USERNAME)
    codeforces_line = get_codeforces_contest_streak(CODEFORCES_USERNAME)
    update_readme([leetcode_line + "\n", codeforces_line + "\n"])
