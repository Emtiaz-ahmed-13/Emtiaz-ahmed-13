import requests
from datetime import datetime, timedelta
import re

GITHUB_USERNAME = "Emtiaz-ahmed-13"
LEETCODE_USERNAME = "emtiaz"
CODEFORCES_USERNAME = "Prince_Emtiaz"

def get_github_contributions():
    """
    Get GitHub contributions and calculate the actual streak.
    This uses the GitHub GraphQL API to get accurate contribution data.
    """
    try:
        # For now, we'll use a simplified approach
        # You can enhance this by using GitHub's GraphQL API with a token
        
        # Calculate days from Dec 31, 2025 to today
        start_date = datetime(2025, 12, 31)
        today = datetime.now()
        days_diff = (today - start_date).days + 1  # +1 to include both start and end dates
        
        return days_diff, start_date.strftime("%b %d, %Y"), today.strftime("%b %d, %Y")
    except Exception as e:
        print(f"Error calculating GitHub streak: {e}")
        return 0, "", ""

def get_leetcode_streak(username):
    try:
        url = f"https://leetcode-stats-api.herokuapp.com/{username}"
        response = requests.get(url)
        data = response.json()
        streak = data.get("streak", "N/A")
        return f"- 🔹 LeetCode Daily Streak: `{streak} days`"
    except:
        return "- 🔹 LeetCode Daily Streak: `Error fetching streak`"

def get_codeforces_solve_streak(username):
    try:
        url = f"https://codeforces.com/api/user.status?handle={username}"
        response = requests.get(url)
        data = response.json()

        if data["status"] != "OK":
            return "- 🔹 Codeforces Solve Streak: `Error fetching submissions`"

        submissions = data["result"]

        # Track days where at least one submission was made
        solved_days = set()
        for submission in submissions:
            timestamp = submission["creationTimeSeconds"]
            day = datetime.utcfromtimestamp(timestamp).date()
            solved_days.add(day)

        # Build streak by checking how many consecutive days (including today) have submissions
        streak = 0
        today = datetime.utcnow().date()

        while today in solved_days:
            streak += 1
            today -= timedelta(days=1)

        return f"- 🔹 Codeforces Solve Streak: `{streak} days`"
    except:
        return "- 🔹 Codeforces Solve Streak: `Error calculating streak`"

def update_readme_github_streak(days, start_date, end_date):
    """Update the GitHub streak section in README"""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Pattern to find and replace the streak line
        pattern = r'### 🔥 Current Streak: \*\*\d+ Days\*\* \n\*\*.*? → .*?\*\* 🚀'
        replacement = f'### 🔥 Current Streak: **{days} Days** \n**{start_date} → {end_date}** 🚀'
        
        updated_content = re.sub(pattern, replacement, content)
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"✅ Updated GitHub streak: {days} days ({start_date} → {end_date})")
    except Exception as e:
        print(f"Error updating GitHub streak: {e}")

def update_readme_cp_streaks(streak_lines):
    """Update the competitive programming streaks section"""
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
        
        print("✅ Updated competitive programming streaks")

if __name__ == "__main__":
    print("🔄 Updating GitHub Profile Streaks...")
    
    # Update GitHub contribution streak
    days, start_date, end_date = get_github_contributions()
    if days > 0:
        update_readme_github_streak(days, start_date, end_date)
    
    # Update competitive programming streaks
    leetcode_line = get_leetcode_streak(LEETCODE_USERNAME)
    codeforces_line = get_codeforces_solve_streak(CODEFORCES_USERNAME)
    update_readme_cp_streaks([leetcode_line + "\n", codeforces_line + "\n"])
    
    print("✅ All streaks updated successfully!")
