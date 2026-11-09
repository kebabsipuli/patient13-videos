"""Saves Roblox's public numbers every hour (run by .github/workflows/stats.yml):
- data/p13_history.csv: Patient 13 players, visits, favorites, likes (kept 90 days)
- data/competitors.csv: the same for similar horror games (kept 7 days)
The Sipuli Studios dashboard reads these files."""
import csv
import datetime
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
P13 = 10774874931
COMPETITORS = {2440500124: "DOORS", 2294168059: "The Mimic", 3761186887: "Apeirophobia",
               4367208330: "Pressure", 5569032992: "Dandy's World", 6331902150: "Forsaken"}
FIELDS = ["time", "universeId", "name", "playing", "visits", "favorites", "upVotes", "downVotes"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sipuli-studios-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def append(path, rows, keep_days):
    old = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            old = list(csv.DictReader(f))
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=keep_days)).isoformat()
    keep = [r for r in old if r["time"] >= cutoff] + rows
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(keep)


ids = [P13] + list(COMPETITORS)
q = ",".join(map(str, ids))
games = {g["id"]: g for g in get("https://games.roblox.com/v1/games?universeIds=" + q)}
votes = {v["id"]: v for v in get("https://games.roblox.com/v1/games/votes?universeIds=" + q)}
now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def row(uid, name):
    g, v = games.get(uid, {}), votes.get(uid, {})
    return {"time": now, "universeId": uid, "name": name, "playing": g.get("playing", ""), "visits": g.get("visits", ""),
            "favorites": g.get("favoritedCount", ""), "upVotes": v.get("upVotes", ""), "downVotes": v.get("downVotes", "")}


append(os.path.join(HERE, "p13_history.csv"), [row(P13, "Patient 13")], 90)
append(os.path.join(HERE, "competitors.csv"), [row(u, n) for u, n in COMPETITORS.items()], 7)
print("saved", now)
