#!/usr/bin/env python3
"""
fleetTEC — AI Visibility Tracker
Queries ChatGPT (OpenAI), Claude (Anthropic), and Gemini (Google)
with brand-relevant prompts and measures how often fleetTEC appears.

Runs via GitHub Actions every Monday. Sends results to Slack.
"""

import json
import os
import time
import datetime
import requests
from pathlib import Path

# ── API keys (loaded from environment / GitHub Secrets) ───────────────────────
OPENAI_API_KEY    = os.environ["OPENAI_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GEMINI_API_KEY    = os.environ["GEMINI_API_KEY"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

# ── Brand detection ───────────────────────────────────────────────────────────
BRAND_VARIANTS = ["fleettec", "fleet tec", "fleettech", "fleet tech"]

# ── Prompts (mapped to fleetTEC's buyers, verticals, and services) ────────────
PROMPTS = [
    # Public Safety — Fleet & Command Staff
    ("Public Safety",   "Who are the best vehicle upfitters for police departments?"),
    ("Public Safety",   "How do I find a company to outfit my police fleet with technology?"),
    ("Public Safety",   "What companies install in-car computers and cameras for law enforcement?"),
    ("Public Safety",   "What should I look for when choosing a vehicle upfitter for my department?"),
    ("Public Safety",   "Who does full-service police vehicle upfitting in the southeast?"),

    # Energy & Utility — Fleet Managers
    ("Energy/Utility",  "Who can upfit utility fleet vehicles with technology and equipment?"),
    ("Energy/Utility",  "Best vehicle upfitting companies for energy and utility fleets?"),
    ("Energy/Utility",  "What companies handle fleet technology installation for utility companies?"),
    ("Energy/Utility",  "How do I find a vendor to manage vehicle upfitting across multiple locations?"),
    ("Energy/Utility",  "Who are the top fleet upfitters for commercial work trucks?"),

    # Public Transportation & Mobile Install
    ("Mobile/Transit",  "Who does mobile vehicle technology installation on site?"),
    ("Mobile/Transit",  "What companies can install fleet technology at our location rather than a shop?"),
    ("Mobile/Transit",  "Who installs cameras and tracking systems on transit buses?"),
    ("Mobile/Transit",  "Best companies for mobile fleet upfitting services?"),
    ("Mobile/Transit",  "Who can handle large-scale vehicle technology deployments on location?"),

    # Panasonic / Partner Channel
    ("Partner Channel", "Who are authorized Panasonic Toughbook installers for fleet vehicles?"),
    ("Partner Channel", "What companies install Panasonic devices in fleet vehicles?"),
    ("Partner Channel", "Who are certified service providers for fleet technology deployment?"),
    ("Partner Channel", "How do I find a partner to deploy Panasonic technology across our fleet?"),
    ("Partner Channel", "Who handles kitting and deployment for fleet technology rollouts?"),

    # Competitive / General Search
    ("Competitive",     "What is vehicle upfitting and who does it?"),
    ("Competitive",     "How do I choose between vehicle upfitting companies?"),
    ("Competitive",     "What is the difference between a vehicle upfitter and a hardware reseller?"),
    ("Competitive",     "Who sells and installs Guardian Angel and Akari vehicle lighting?"),
    ("Competitive",     "What companies do both vehicle graphics and technology upfitting?"),
]

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ── Brand mention check ───────────────────────────────────────────────────────

def brand_mentioned(text: str) -> bool:
    t = text.lower()
    return any(v in t for v in BRAND_VARIANTS)


# ── Historical data helpers ───────────────────────────────────────────────────

def load_previous_week() -> dict | None:
    files = sorted(DATA_DIR.glob("week_*.json"))
    if len(files) >= 1:
        with open(files[-1]) as f:
            return json.load(f)
    return None


def save_results(results: dict):
    today = datetime.date.today().isoformat()
    path = DATA_DIR / f"week_{today}.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    return path


# ── Platform query functions ──────────────────────────────────────────────────

def query_openai(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
    }
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions",
                          json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"


def query_anthropic(prompt: str) -> str:
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 800,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
                          json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"ERROR: {e}"


def query_gemini(prompt: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"ERROR: {e}"


# ── Main tracker ──────────────────────────────────────────────────────────────

def run_tracker() -> dict:
    print("🔍 Running fleetTEC AI Visibility Tracker...")
    week_start = datetime.date.today().isoformat()

    results = {
        "week": week_start,
        "platforms": {"chatgpt": [], "claude": [], "gemini": []},
        "summary": {},
    }

    platforms = [
        ("chatgpt", query_openai),
        ("claude",  query_anthropic),
        ("gemini",  query_gemini),
    ]

    for platform_name, query_fn in platforms:
        print(f"\n  [{platform_name.upper()}] Querying {len(PROMPTS)} prompts...")
        for i, (category, prompt) in enumerate(PROMPTS):
            print(f"    {i+1}/{len(PROMPTS)}: {prompt[:65]}...")
            response = query_fn(prompt)
            mentioned = brand_mentioned(response) if not response.startswith("ERROR") else False
            results["platforms"][platform_name].append({
                "category": category,
                "prompt": prompt,
                "mentioned": mentioned,
                "error": response.startswith("ERROR"),
                "response_snippet": response[:300],
            })
            time.sleep(0.4)

        hits = sum(1 for r in results["platforms"][platform_name] if r["mentioned"])
        print(f"    → fleetTEC mentioned in {hits}/{len(PROMPTS)} responses")

    # ── Compute summary ───────────────────────────────────────────────────────
    total_queries = len(PROMPTS) * 3
    total_hits = sum(
        1 for pdata in results["platforms"].values()
        for r in pdata if r["mentioned"]
    )

    per_platform = {}
    for pname, pdata in results["platforms"].items():
        hits = sum(1 for r in pdata if r["mentioned"])
        per_platform[pname] = {
            "hits": hits,
            "total": len(PROMPTS),
            "pct": round(hits / len(PROMPTS) * 100),
        }

    prompt_map: dict[str, dict] = {}
    for pname, pdata in results["platforms"].items():
        for r in pdata:
            key = r["prompt"]
            if key not in prompt_map:
                prompt_map[key] = {"category": r["category"], "platforms": []}
            if r["mentioned"]:
                prompt_map[key]["platforms"].append(pname)

    winning = {k: v for k, v in prompt_map.items() if v["platforms"]}
    gaps    = {k: v for k, v in prompt_map.items() if not v["platforms"]}

    prev = load_previous_week()
    wow_delta = None
    if prev and "summary" in prev:
        prev_pct = prev["summary"].get("overall_pct", 0)
        wow_delta = round(total_hits / total_queries * 100) - prev_pct

    results["summary"] = {
        "total_hits":      total_hits,
        "total_queries":   total_queries,
        "overall_pct":     round(total_hits / total_queries * 100),
        "per_platform":    per_platform,
        "winning_prompts": winning,
        "gap_prompts":     gaps,
        "wow_delta":       wow_delta,
    }

    save_results(results)
    print(f"\n✅ Done — Overall: {total_hits}/{total_queries} ({results['summary']['overall_pct']}%)")
    return results


# ── Slack formatter ───────────────────────────────────────────────────────────

def format_slack_message(results: dict) -> str:
    s = results["summary"]
    week = results["week"]

    if s["wow_delta"] is None:
        delta_str = "_baseline week — tracking starts now_"
    elif s["wow_delta"] > 0:
        delta_str = f"↑ +{s['wow_delta']}% vs last week 🟢"
    elif s["wow_delta"] < 0:
        delta_str = f"↓ {s['wow_delta']}% vs last week 🔴"
    else:
        delta_str = "→ flat vs last week 🟡"

    label = {"chatgpt": "ChatGPT", "claude": "Claude", "gemini": "Gemini"}
    lines = [
        f"🚛 *fleetTEC AI Visibility Report* — Week of {week}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"*Overall: {s['total_hits']}/{s['total_queries']} prompts ({s['overall_pct']}%)* — {delta_str}",
        "",
        "*By Platform:*",
    ]
    for pname, pdata in s["per_platform"].items():
        filled = "█" * (pdata["pct"] // 10)
        empty  = "░" * (10 - pdata["pct"] // 10)
        lines.append(
            f"  • {label[pname]}: {pdata['hits']}/{pdata['total']} ({pdata['pct']}%)  `{filled}{empty}`"
        )

    if s["winning_prompts"]:
        lines += ["", "*✅ Prompts Where fleetTEC Appeared:*"]
        for prompt, info in list(s["winning_prompts"].items())[:8]:
            plats = ", ".join(info["platforms"])
            lines.append(f"  • _{prompt[:72]}_ ({plats})")
    else:
        lines += ["", "*✅ Prompts Where fleetTEC Appeared:* None this week — keep publishing!"]

    priority = ["Public Safety", "Energy/Utility", "Mobile/Transit", "Partner Channel", "Competitive"]
    gaps_sorted = sorted(
        s["gap_prompts"].items(),
        key=lambda x: priority.index(x[1]["category"]) if x[1]["category"] in priority else 99,
    )
    lines += ["", f"*❌ Visibility Gaps — {len(s['gap_prompts'])} prompts with no mention:*"]
    for prompt, info in gaps_sorted[:6]:
        lines.append(f"  • _{prompt[:72]}_ ({info['category']})")
    if len(gaps_sorted) > 6:
        lines.append(f"  _...and {len(gaps_sorted) - 6} more_")

    lines += [
        "",
        "_Platforms: ChatGPT · Claude · Gemini · 25 prompts each · 75 total queries_",
    ]
    return "\n".join(lines)


# ── Slack delivery ────────────────────────────────────────────────────────────

def send_to_slack(message: str):
    payload = {"text": message}
    r = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
    if r.status_code == 200:
        print("✅ Report sent to Slack")
    else:
        print(f"⚠️  Slack delivery failed: {r.status_code} {r.text}")
        raise SystemExit(1)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = run_tracker()
    message = format_slack_message(results)
    print("\n── SLACK REPORT PREVIEW ─────────────────────────────────────")
    print(message)
    print("─────────────────────────────────────────────────────────────")
    send_to_slack(message)
