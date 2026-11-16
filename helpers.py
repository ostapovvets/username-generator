import requests
from generator import HOST, DEFAULT_MODEL, groups, generate_usernames
from platforms import PLATFORMS, check_roblox

#every setting the user can change on the page
LIMITS = {
    "count":       (5, 50, 15),
    "examples":    (5, 30, 15),
    "temperature": (0.1, 1.5, 0.8),
}


#check whcih models are installed

def get_models():
    try:
        r = requests.get(f"http://{HOST}:11434/api/tags", timeout=3)
        return [m["name"] for m in r.json()["models"]]
    except (requests.RequestException, KeyError, ValueError):
        return []


#NEVER trust the input from the web page

def clamp(value, setting):
    low, high, default = LIMITS[setting]

    try:
        value = float(value)
    except (TypeError, ValueError):
        return default

    if value < low:
        return low
    if value > high:
        return high
    return value



def run(style=None, platform=None, model=None, count=None, examples_count=None, temperature=None):
    #check every setting, fall back to defaults
    if style not in groups:
        style = "clean_word"
    if platform not in PLATFORMS:
        platform = "any"
    if model not in get_models():
        model = DEFAULT_MODEL
    count = int(clamp(count, "count"))
    examples_count = int(clamp(examples_count, "examples"))
    temperature = clamp(temperature, "temperature")

    names, rejected, error = generate_usernames(style, platform, model, count, examples_count, temperature)

    #check availability (only roblox for nmow)
    if platform == "roblox":
        statuses = check_roblox(names)
    else:
        statuses = {}
        for n in names:
            statuses[n] = "not checked"

    #one small dictionary per name so the web page gets name + status together
    results = []
    for n in names:
        results.append({"name": n, "status": statuses[n]})

    return {
        "names": results,
        "rejected": rejected,
        "error": error,
        "settings": {"style": style, "platform": platform, "model": model, "count": count,
                     "examples_count": examples_count, "temperature": temperature},
    }


#test

if __name__ == "__main__":
    print("Installed models:", get_models())
    result = run(style="clean_word", platform="roblox", count=15, examples_count=30, temperature=0.8)

    if result["error"]:
        print("ERROR:", result["error"])
    for r in result["names"]:
        print(f"{r['name']:<20} {r['status']}")
    print("\nrejected:", result["rejected"])
    print("settings:", result["settings"])
