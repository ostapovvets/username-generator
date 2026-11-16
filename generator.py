import subprocess
import ollama
import sys
import random
from difflib import get_close_matches
from data import cleaned_names
import csv
from platforms import PLATFORMS, clean_name, valid

# if cleaned names is empty

if not cleaned_names:
    sys.exit("No valid names found")

#get host ip
def get_host():
    try:
        return subprocess.check_output("ip route show default | awk '{print $3}'",shell=True,text=True).strip()
    except Exception as r:
        print(f"Failed to get host ip, defaulting to localhost. Error : {r}")
        return "localhost"

HOST = get_host()
client = ollama.Client(host=f"http://{HOST}:11434")

# gdjkfghfk

DEFAULT_MODEL = "name-engine"
#model = "llama3.1"
#model = "mistral-nemo:12b"

MAX_TRIES = 3

USE_EXTRA_FILTERS = True

CLICHES = ["flux", "nebul", "lumin", "nex", "aether", "aero", "crypt", "nova", "void", "cyber", "spectr", "echo", "cryo", "vortex"]
#CLICHES = []

LOWERCASE_CHANCE = 0 #0 - turned off

#real english words

try:
    with open("/usr/share/dict/words") as f:
        real_words = {w.strip().lower() for w in f}
except FileNotFoundError:
    print ("Word list not found, skipped")
    real_words = set()


#load the csv once into {style: [names]}

groups = {}
with open("thematic_usernames.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        style = row["style"]
        #first time we see this style, give it an empty list
        if style not in groups:
            groups[style] = []
        groups[style].append(row["username"])


STYLE_GUIDES = {
    "clean_word": "Style constraint: Generate smooth, single-word usernames. They should look like English dictionary words, clean pseudo-words, or sleek single-word handles (e.g. upbraided, Acquiredly). Avoid numbers or underscores.",
    "compound_phrase": "Style constraint: Generate compound concept phrase usernames (CamelCase concepts, combined words, or phrases connected by single underscores, e.g. HyperAbilities, DoNoRight).",
    "short_tag": "Style constraint: Generate ultra-short vintage handles that are between 2 and 5 characters in length (e.g. tqaz, r_ab, h0w6).",
    "alphanumeric_id": "Style constraint: Generate serial codes, bot-like identifiers, or usernames padded/ending with numerical characters (e.g. Bestlocker67, roblox_user_8880765753).",
    "abstract_glitch": "Style constraint: Generate abstract glitch patterns, repeating matrix character blocks, barcode handles, or keyboard-noise sequences (e.g. xzxvxzxvxzxv, IlllllllIIIlllIIIllI).",
}

known_lower = [n.lower() for n in cleaned_names]


# build a prompt

def build_prompt(examples, count, style, platform):
    return(
        "You are an expert username generation engine. "
        "Your task is to generate UNIQUE, cool, clean, and catchy usernames that mimic the aesthetic and patterns of the examples provided. "
        f"\n{STYLE_GUIDES.get(style, '')}\n"
        f"{PLATFORMS[platform]['rules']}\n"
        "Input style examples:\n"
        f"{examples}\n\n"
        "Generate EXACTLY the requested number of usernames. "
        "Respond ONLY with the list of generated usernames, one per line. Do not write any explanations, numbering, notes, or introductions."
        f"\n\nUser Prompt: Generate {count} unique usernames.\n\nUsernames:\n"
    )




def generate_usernames(style, platform, model, count, examples_count, temperature):
    good = []
    rejected = {"invalid": 0, "duplicate": 0, "exact_copy": 0, "near_copy": 0, "borrowed": 0, "cliche": 0, "real_word": 0}
    tries = 0
    options = {"temperature": temperature}
    pool = groups[style]   #examples come from the chosen style

    while len(good) < count and tries < MAX_TRIES:
        tries += 1

        shown = random.sample(pool, min(examples_count, len(pool)))   #min() because some styles are small
        shown_lower = [s.lower() for s in shown]
        examples = ", ".join(shown)
        prompt = build_prompt(examples, count, style, platform)

        try:
            response = client.generate(model=model, prompt=prompt, options=options)
            candidates = response.response.splitlines()
        except Exception as e:
            #fixed -return an error instead of sys.exit, which would shut down the whole server
            return good, rejected, f"Could not reach the model: {e}"

        for raw in candidates:
            name = clean_name(raw, platform)
            lower = name.lower()

            if not name:
                continue

            if not valid(name, platform):
                rejected["invalid"] += 1
                continue

            if lower in [g.lower() for g in good]:
                rejected["duplicate"] += 1
                continue

            if USE_EXTRA_FILTERS:
                if lower in known_lower:
                    rejected["exact_copy"] += 1
                    continue
                if get_close_matches(lower, known_lower, n=1, cutoff=0.85):
                    rejected["near_copy"] += 1
                    continue

                #if built out of a piece of one of the examples given
                if any(len(s) >= 5 and s[:5] in lower for s in shown_lower):
                    rejected["borrowed"] += 1
                    continue
                if any(c in lower for c in CLICHES):
                    rejected["cliche"] += 1
                    continue
                if lower in real_words:
                    rejected["real_word"] += 1
                    continue

            if random.random() < LOWERCASE_CHANCE:
                name = name.lower()

            good.append(name)

    return good[:count], rejected, None


#test

if __name__ == "__main__":
    names, rejected, error = generate_usernames("clean_word", "roblox", DEFAULT_MODEL, 15, 30, 0.8)
    if error:
        print(error)
    print("\n".join(names))
    print(rejected)
