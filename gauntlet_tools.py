import glob
import hashlib
import json
import math
import os
import requests

from deck_list_manager import get_card_entry
from mtg_deck import MTGDeck
from mtg_tools import get_card_type
from visualization_tools import visual_spoiler_v2

current_dir = os.path.dirname(os.path.abspath(__file__))
deck_list_path = os.path.join(current_dir, "deck_lists")
pre_gauntlet_deck_list_path = os.path.join(current_dir, "pre_gauntlet_deck_lists")
image_path = os.path.join(current_dir, "deck_images")


def save_deck_to_json(deck, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(deck, file, indent=4)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def ensure_cache_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def build_gauntlet(list_of_decks, filename="gauntlet.json"):
    total_cards = 0
    gauntlet_list = {"cards": []}
    cards_used = {}
    for deck in list_of_decks:
        cards_needed = deck.get_cards_needed()
        for card_name, quantity in cards_needed.items():
            if card_name in cards_used:
                cards_used[card_name].append(quantity)
            else:
                cards_used[card_name] = [quantity]

    for card in cards_used:
        cards_used[card] = sorted(cards_used[card], reverse=True)

    for name, quantities in cards_used.items():
        if len(quantities) == 1:
            total_needed = quantities[0]
        else:
            total_needed = quantities[0] + quantities[1]
        card = {"name": name, "quantity": total_needed}
        total_cards += total_needed
        gauntlet_list["cards"].append(card)

    save_deck_to_json(gauntlet_list, filename)


def create_or_load_deck(raw_deck):
    # Ensure the deck_cache directory exists
    cache_directory = "deck_cache"
    ensure_cache_directory(cache_directory)

    # Calculate the hash for the raw_deck before creating the object
    deck_hash = hashlib.md5(str(raw_deck).encode()).hexdigest()
    cache_file = os.path.join(cache_directory, f"deck_cache_{deck_hash}.pkl")

    # Check if the deck is already cached
    cached_deck = MTGDeck.load_from_cache(cache_file)
    if cached_deck:
        print("Loaded deck from cache.")
        return cached_deck

    # If not cached, create a new deck and cache it
    print("Creating new deck and saving to cache.")
    new_deck = MTGDeck(raw_deck)
    new_deck.save_to_cache(cache_file)
    return new_deck


def compare_cards(json1, json2):
    cards1 = {card["name"]: card["quantity"] for card in json1["cards"]}
    cards2 = {card["name"]: card["quantity"] for card in json2["cards"]}

    all_cards = set(cards1.keys()).union(set(cards2.keys()))

    differences = []
    for card in all_cards:
        quantity1 = cards1.get(card, 0)
        quantity2 = cards2.get(card, 0)

        if quantity1 != quantity2:
            differences.append(
                {
                    "name": card,
                    "quantity_in_file1": quantity1,
                    "quantity_in_file2": quantity2,
                }
            )

    return differences


def print_differences(differences):
    if not differences:
        print("No differences found.")
        return

    for diff in differences:
        print(
            f"{int(diff['quantity_in_file2']) - int(diff['quantity_in_file1'])} {diff['name']}"
        )


def differences_to_dict(differences):
    if not differences:
        return {}

    diff_dict = {}
    for diff in differences:
        diff_dict[diff["name"]] = diff["quantity_in_file2"] - diff["quantity_in_file1"]
    return diff_dict


def build_deck_lists(which_decks="gauntlet"):
    print("Building Deck Lists")
    if which_decks == "gauntlet":
        txt_files = glob.glob(os.path.join(deck_list_path, "*.txt"))
    else:
        txt_files = glob.glob(os.path.join(pre_gauntlet_deck_list_path, "*.txt"))
    decks = []
    deck_names = []
    for txt_file in txt_files:
        with open(txt_file, "r", encoding="utf-8") as file:
            current_deck = file.readlines()
            deck_names.append(current_deck[0].strip())
        d = create_or_load_deck(current_deck)
        decks.append(d)
        print(current_deck[0].strip(), "Build")
    return decks


def update_deck_visuals(deck_lists):
    for deck in deck_lists:
        for version in deck.mainboard.keys():
            # deck_list = deck.mainboard[version]
            # sideboard_list = deck.sideboard[version]
            deck_name = deck.deck_name[version] + " " + version
            # visual_spoiler_v2(deck_list, sideboard_list, deck_name, version, deck)
            visual_spoiler_v2(deck, version)
            print(deck_name, version, "Visual done")


def generate_token_html(card_name, uri):
    html = ""
    layout = uri.get("layout", None)
    if layout == "token" or layout == "flip":
        img_url = uri["image_uris"]["large"]
        html = f'<li><span class="card">{card_name} <img src="{img_url}" alt="{card_name}"> </span></li>'
    elif layout == "double_faced_token":
        img_url_front = uri["card_faces"][0]["image_uris"]["large"]
        img_url_back = uri["card_faces"][1]["image_uris"]["large"]
        html = f'<li><span class="card">{card_name} <img src="{img_url_front}" alt="{card_name}" class="front"> <img src="{img_url_back}" alt="{card_name}" class="back"> </span></li>'
    elif layout == "emblem":
        img_url = uri["image_uris"]["large"]
        html = f'<li><span class="card">{card_name} <img src="{img_url}" alt="{card_name}"> </span></li>'
    else:
        return f"Token layout not supported: {layout}"

    return html


def generate_token_list(deck, version="v1"):
    token_html = []
    for item in deck.mainboard[version]:
        card = get_card_entry(item)
        card_parts = card.get("all_parts", [])
        for part in card_parts:
            component = part.get("component", None)
            if component == "token":
                uri = requests.get(part["uri"]).json()
                token_html.append(generate_token_html(part["name"], uri))
            if component == "combo_piece" and "Emblem" in part.get("type_line", ""):
                uri = requests.get(part["uri"]).json()
                token_html.append(generate_token_html(part["name"], uri))
    for item in deck.sideboard.get(version, {}):
        card = get_card_entry(item)
        card_parts = card.get("all_parts", [])
        for part in card_parts:
            component = part.get("component", None)
            if component == "token":
                uri = requests.get(part["uri"]).json()
                token_html.append(generate_token_html(part["name"], uri))
            if component == "combo_piece" and "Emblem" in part.get("type_line", ""):
                uri = requests.get(part["uri"]).json()
                token_html.append(generate_token_html(part["name"], uri))
    token_html.sort()
    for item in token_html:
        print(item)
    print("\n\n")


def deck_distance(deck1, deck2):
    deck1_nonlands = [card for card in deck1 if get_card_type(card) != "Land"]
    deck2_nonlands = [card for card in deck2 if get_card_type(card) != "Land"]
    common_cards = set()
    for card in deck1_nonlands:
        if card in deck2_nonlands:
            common_cards.add(card)
    dist = (
        max(
            len(common_cards) / len(deck1_nonlands),
            len(common_cards) / len(deck2_nonlands),
        )
        * 100
    )
    return math.floor(dist)
