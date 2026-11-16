import re
import requests

LETTERS_AND_DIGITS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

PLATFORMS = {
    "any": {
        "rules": "Username rules:\n- Length between 3 and 20 characters.\n- Letters and numbers only, one word.\n",
        "min": 3, "max": 20,
        "sep": "",
        "allowed": LETTERS_AND_DIGITS,
    },
    "roblox": {
        "rules": "Strict Roblox Username Rules:\n- Length must be between 3 and 20 characters.\n- Alphanumeric characters and single underscores only.\n- Cannot start or end with an underscore.\n- No consecutive underscores (no '__').\n",
        "min": 3, "max": 20,
        "sep": "_",
        "allowed": LETTERS_AND_DIGITS + "_",
    },
    "tiktok": {
        "rules": "Strict TikTok Username Rules:\n- Length between 2 and 24 characters.\n- Letters, numbers, underscores and periods only.\n- Cannot end with a period.\n",
        "min": 2, "max": 24,
        "sep": "_",
        "allowed": LETTERS_AND_DIGITS + "_.",
    },
}


#clean a raw line from the model into a name that fits the platforms characters

def clean_name(raw, platform):
    p = PLATFORMS[platform]

    #remove junk
    name = re.sub(r"^\s*(\d+[.)]|[-*])\s+", "", raw.strip()).strip("'\"[]()")

    #spaces, hyphens and underscores become the platform's separator
    for c in " -_":
        name = name.replace(c, p["sep"])

    #keep only the characters the platform allows
    new_name = ""
    for c in name:
        if c in p["allowed"]:
            new_name += c
    return new_name


#check if a name follows the platforms rules

def valid(name, platform):
    p = PLATFORMS[platform]
    if not (p["min"] <= len(name) <= p["max"]):
        return False
    if platform == "roblox" and (name.startswith("_") or name.endswith("_") or "__" in name):
        return False
    if platform == "tiktok" and (name.endswith(".") or ".." in name):
        return False
    return True


#roblox availability check

def check_roblox(names):
    statuses = {}

    try:
        response = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": names, "excludeBannedUsers": False},
            timeout=10,
        )
    except requests.RequestException:
        response = None

#no answer or anything other than 200 means we dont know and fall back to couldnt check
    if response is None or response.status_code != 200:
        for n in names:
            statuses[n] = "couldn't check"
        return statuses

    taken = []
    for user in response.json()["data"]:
        taken.append(user["requestedUsername"].lower())

    for n in names:
        if n.lower() in taken:
            statuses[n] = "taken"
        else:
            statuses[n] = "available"
    return statuses
