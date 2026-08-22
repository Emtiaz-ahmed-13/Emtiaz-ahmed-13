import json
import os
import re
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# =========================
# USER CONFIG
# =========================
GITHUB_USERNAME = "Emtiaz-ahmed-13"
LEETCODE_USERNAME = "emtiaz"
CODEFORCES_USERNAME = "Prince_Emtiaz"
README_FILE = "README.md"

# Optional: dates repaired with LeetCode streak freeze / time travel
LEETCODE_MANUAL_FILL_DATES = [
    "2025-07-17",
    "2025-07-11",
]

UA = "Mozilla/5.0 (compatible; streak-updater/2.0; +https://github.com/Emtiaz-ahmed-13)"


def utc_today():
    return datetime.now(timezone.utc).date()


def http_get(url, headers=None, timeout=20):
    req = Request(url, headers=headers or {"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def http_post_json(url, payload, headers=None, timeout=20):
    body = json.dumps(payload).encode("utf-8")
    merged = {"User-Agent": UA, "Content-Type": "application/json"}
    if headers:
        merged.update(headers)
    req = Request(url, data=body, headers=merged)
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def current_streak(solved_days, today=None):
    """Count consecutive days ending today, or yesterday if today is still empty."""
    if not solved_days:
        return 0

    today = today or utc_today()
    yesterday = today - timedelta(days=1)

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


# =========================
# GITHUB STREAK
# =========================
def get_github_streak(username):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        try:
            return _github_streak_graphql(username, token)
        except Exception as e:
            print(f"⚠️ GitHub GraphQL failed, using public API: {e}")

    return _github_streak_public_api(username)


def _github_streak_graphql(username, token):
    payload = {
        "query": """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """,
        "variables": {"login": username},
    }
    data = http_post_json(
        "https://api.github.com/graphql",
        payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )
    if data.get("errors"):
        raise RuntimeError(data["errors"])

    weeks = (
        data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    )
    solved = set()
    for week in weeks:
        for day in week["contributionDays"]:
            if day["contributionCount"] > 0:
                solved.add(datetime.strptime(day["date"], "%Y-%m-%d").date())
    return current_streak(solved)


def _github_streak_public_api(username):
    raw = http_get(f"https://github-contributions-api.jogruber.de/v4/{username}")
    data = json.loads(raw)
    solved = {
        datetime.strptime(item["date"], "%Y-%m-%d").date()
        for item in data.get("contributions", [])
        if item.get("count", 0) > 0
    }
    return current_streak(solved)


# =========================
# LEETCODE STREAK
# =========================
def get_leetcode_stats(username):
    """Return (streak, solved_count). Uses official GraphQL; Heroku mirror is often down."""
    year = utc_today().year
    payload = {
        "query": """
        query userProfileCalendar($username: String!, $year: Int) {
          matchedUser(username: $username) {
            submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
              }
            }
            userCalendar(year: $year) {
              streak
              submissionCalendar
            }
          }
        }
        """,
        "variables": {"username": username, "year": year},
    }
    data = http_post_json(
        "https://leetcode.com/graphql",
        payload,
        headers={"Referer": "https://leetcode.com/", "Origin": "https://leetcode.com"},
    )
    user = (data.get("data") or {}).get("matchedUser")
    if not user:
        raise RuntimeError(f"LeetCode user not found: {username}")

    solved = 0
    for row in user.get("submitStatsGlobal", {}).get("acSubmissionNum") or []:
        if row.get("difficulty") == "All":
            solved = int(row.get("count") or 0)

    calendar = user.get("userCalendar") or {}
    api_streak = calendar.get("streak")
    raw_cal = calendar.get("submissionCalendar") or "{}"
    if isinstance(raw_cal, str):
        raw_cal = json.loads(raw_cal)

    solved_days = set()
    for ts_str in raw_cal.keys():
        solved_days.add(datetime.fromtimestamp(int(ts_str), tz=timezone.utc).date())

    for date_str in LEETCODE_MANUAL_FILL_DATES:
        try:
            solved_days.add(datetime.strptime(date_str, "%Y-%m-%d").date())
        except ValueError:
            pass

    computed = current_streak(solved_days)
    # LeetCode's streak field includes freeze / time-travel; calendar gaps
    # would otherwise under-count. Use computed only if the API omits it.
    streak = int(api_streak or 0) or computed
    return streak, solved


# =========================
# CODEFORCES STREAK
# =========================
def get_codeforces_streak(username):
    raw = http_get(
        f"https://codeforces.com/api/user.status?handle={username}&from=1&count=5000"
    )
    data = json.loads(raw)
    if data.get("status") != "OK":
        raise RuntimeError(data.get("comment") or "Codeforces API error")

    solved_days = set()
    for sub in data.get("result") or []:
        if sub.get("verdict") != "OK":
            continue
        day = datetime.fromtimestamp(sub["creationTimeSeconds"], tz=timezone.utc).date()
        solved_days.add(day)

    return current_streak(solved_days)


# =========================
# UPDATE README
# =========================
def replace_badge_days(content, platform, days):
    """Match shields.io badges like 🏆_LEETCODE-240_DAYS or 😺_GITHUB-31_DAYS."""
    pattern = rf"(badge/[^\"'\s]*{platform}-)\d+(_DAYS)"
    updated, n = re.subn(pattern, rf"\g<1>{days}\g<2>", content, flags=re.IGNORECASE)
    if n == 0:
        print(f"⚠️ No {platform} badge found in README.md")
    return updated


def update_readme(github_days, leetcode_days, codeforces_days, leetcode_solved=None):
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if github_days is not None:
        content = replace_badge_days(content, "GITHUB", github_days)
    if leetcode_days is not None:
        content = replace_badge_days(content, "LEETCODE", leetcode_days)
        content = re.sub(
            r"\(\d+[+\-\s]*day LeetCode streak\)",
            f"({leetcode_days}-day LeetCode streak)",
            content,
        )
    if codeforces_days is not None:
        content = replace_badge_days(content, "CODEFORCES", codeforces_days)
    if leetcode_solved is not None:
        content = re.sub(
            r"✅\s*\d+\+?\s*Problems Solved",
            f"✅ {leetcode_solved}+ Problems Solved",
            content,
        )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def fetch_or_skip(label, fn):
    try:
        value = fn()
        print(f"✅ {label}: {value}")
        return value
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError, KeyError) as e:
        print(f"⚠️ {label} skipped ({e})")
        return None
    except Exception as e:
        print(f"⚠️ {label} skipped ({e})")
        return None


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🔄 Updating GitHub profile streaks...\n")

    github_streak = fetch_or_skip(
        "GitHub streak", lambda: get_github_streak(GITHUB_USERNAME)
    )

    leetcode_streak = None
    leetcode_solved = None

    def _leetcode():
        streak, solved = get_leetcode_stats(LEETCODE_USERNAME)
        return streak, solved

    lc = fetch_or_skip("LeetCode stats", _leetcode)
    if lc is not None:
        leetcode_streak, leetcode_solved = lc
        print(f"   streak={leetcode_streak}, solved={leetcode_solved}")

    codeforces_streak = fetch_or_skip(
        "Codeforces streak", lambda: get_codeforces_streak(CODEFORCES_USERNAME)
    )

    update_readme(github_streak, leetcode_streak, codeforces_streak, leetcode_solved)
    print("\n✅ README.md updated")
