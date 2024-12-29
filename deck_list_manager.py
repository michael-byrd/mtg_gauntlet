import json
import requests
import time
import os
import glob

current_dir = os.path.dirname(os.path.abspath(__file__))
deck_list_path = os.path.join(current_dir, 'deck_lists')

with open('oracle-cards-20240723210312.json', 'r', encoding="utf8") as f:
    oracle_data = json.load(f)

def get_card_entry(card_name):
    for card in oracle_data:
        if card['name'].lower() == card_name.lower():
            if card['set_type'] != "funny":
                return card
    url = 'https://api.scryfall.com/cards/named?fuzzy=' + card_name
    fuzzy_response = requests.get(url)
    return fuzzy_response.json()

def get_oracle_name(card_name):
    url = 'https://api.scryfall.com/cards/named?fuzzy=' + card_name
    # Wait for 100ms to avoid rate limiting
    time.sleep(0.2)
    response = requests.get(url)
    data = response.json()
    # print(card_name, data)
    return data['name']

def get_card_colors(card_name):
    card = get_card_entry(card_name)
    layout = card['layout']
    if layout == "adventure":
        return card['color_identity']
    elif layout == "transform":
        return card['card_faces'][0]['colors']
    elif layout == "modal_dfc":
        colors = []
        for face in card['card_faces']:
            colors += face['colors']
        return list(set(colors))
    elif layout == "prototype":
        return card['color_identity']
    else:
        return card['colors']

class deck:
    def __init__(self, raw_deck):
        self.mainboard = {}
        self.sideboard = {}
        self.deck_name = None
        self.raw_deck = raw_deck
        self.build_deck_list()

    def build_deck_list(self):
        self.deck_name = self.raw_deck[0].strip()
        content = ''.join(self.raw_deck[1:])
        sections = content.split('# v')
        versions = {}
        for section in sections:
            if section.strip():
                version, cards = section.split('\n', 1)
                versions[f'v{version.strip()}'] = cards.strip().split('\n')

        for version, cards in versions.items():
            version_mainboard = {}
            version_sideboard = {}
            if "# Sideboard" in cards:
                main_raw_deck = cards[:cards.index("# Sideboard")]
                sideboard_raw_deck = cards[cards.index("# Sideboard") + 1:]
            else:
                main_raw_deck = cards[0:]
                sideboard_raw_deck = []
            for card in main_raw_deck:
                card_count, name = card.split(" ", 1)
                name = get_oracle_name(name)
                version_mainboard[name] = int(card_count)
            for card in sideboard_raw_deck:
                card_count, name = card.split(" ", 1)
                name = get_oracle_name(name)
                version_sideboard[name] = int(card_count)
            self.mainboard[version] = version_mainboard
            self.sideboard[version] = version_sideboard

    def get_cards_needed(self):
        cards_needed = {}
        for version in self.mainboard:
            for card_name, quantity in self.mainboard[version].items():
                if card_name in cards_needed:
                    cards_needed[card_name] = max(cards_needed[card_name], quantity)
                else:
                    cards_needed[card_name] = quantity
        cards_needed_sideboard = {}
        for version in self.sideboard:
            for card_name, quantity in self.sideboard[version].items():
                if card_name in cards_needed_sideboard:
                    cards_needed_sideboard[card_name] = max(cards_needed_sideboard[card_name], quantity)
                else:
                    cards_needed_sideboard[card_name] = quantity
        for card_name, quantity in cards_needed_sideboard.items():
            if card_name in cards_needed:
                cards_needed[card_name] += quantity
            else:
                cards_needed[card_name] = quantity
        return cards_needed

    def get_color_distribution(self):
        color_distribution = {}
        for card_name, quantity in self.mainboard.items():
            card_colors = get_card_colors(card_name)
            print(card_name, card_colors)
            for c in card_colors:
                if c in color_distribution:
                    color_distribution[c] += quantity
                else:
                    color_distribution[c] = quantity
        print(color_distribution)


### Implementing things, we should do this somewhere else. ###

txt_files = glob.glob(os.path.join(deck_list_path, '*.txt'))
decks = []
deck_names = []
for txt_file in txt_files:
    with open(txt_file, 'r') as file:
        current_deck = file.readlines()
        # print(current_deck)
        deck_names.append(current_deck[0].strip())
    # d = deck(current_deck)
    # print(d.deck_name)
    # decks.append(d)



# from test_file import *
#
# for deck in decks:
#     for version in deck.mainboard.keys():
#         deck_list = deck.mainboard[version]
#         sideboard_list = deck.sideboard[version]
#         deck_name = deck.deck_name.removeprefix("# ")
#         print(deck_list)
#         visual_spoiler_v2(deck_list, sideboard_list, deck_name)


import random
print(deck_names)
print(random.choice(deck_names))

##############################################################


# build_gauntlet uses this.
def save_deck_to_json(deck, filename):
    with open(filename, 'w') as file:
        json.dump(deck, file, indent=4)

# May not need.
def read_text_file_to_dict(file_path):
    data_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith('#'):
                continue
            quantity, name = line.split(' ', 1)
            name = get_oracle_name(name)
            if name in data_dict:
                data_dict[name].append(int(quantity))
            else:
                data_dict[name] = [int(quantity)]
    return data_dict

# May not need.
def build_deck_list(file_path, deck_name="Example Deck"):
    deck_list = {
        "deck_name": deck_name,
        "cards": []
    }

    data_dict = read_text_file_to_dict(file_path)

    for name, quantity in data_dict.items():
        card = {
            "name": name,
            "quantity": quantity
        }
        deck_list["cards"].append(card)

    save_deck_to_json(deck_list, f"{deck_name}.json")


def build_gauntlet(list_of_decks):
    total_cards = 0
    gauntlet_list = {
        "cards": []
    }
    cards_used = {}
    for deck in list_of_decks:
        cards_needed = deck.get_cards_needed()
        # print(cards_needed)
        for card_name, quantity in cards_needed.items():
            if card_name in cards_used:
                cards_used[card_name].append(quantity)
            else:
                cards_used[card_name] = [quantity]

    for item in cards_used:
        cards_used[item] = sorted(cards_used[item], reverse=True)

    for name, quantities in cards_used.items():
        # print(name, quantities)
        if len(quantities) == 1:
            total_needed = quantities[0]
        else:
            total_needed = quantities[0] + quantities[1]
        card = {
            "name": name,
            "quantity": total_needed
        }
        total_cards += total_needed
        gauntlet_list["cards"].append(card)

    save_deck_to_json(gauntlet_list, "gauntlet.json")


# build_gauntlet(decks)


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def compare_cards(json1, json2):
    cards1 = {card['name']: card['quantity'] for card in json1['cards']}
    cards2 = {card['name']: card['quantity'] for card in json2['cards']}

    all_cards = set(cards1.keys()).union(set(cards2.keys()))

    differences = []
    for card in all_cards:
        quantity1 = cards1.get(card, 0)
        quantity2 = cards2.get(card, 0)

        if quantity1 != quantity2:
            differences.append({
                'name': card,
                'quantity_in_file1': quantity1,
                'quantity_in_file2': quantity2
            })

    return differences


def print_differences(differences):
    if not differences:
        print("No differences found.")
        return

    for diff in differences:
        print(str(int(diff['quantity_in_file2']) - int(diff['quantity_in_file1'])) + " " + diff['name'])
        # print(f"Card: {diff['name']}")
        # print(f"  Quantity in file 1: {diff['quantity_in_file1']}")
        # print(f"  Quantity in file 2: {diff['quantity_in_file2']}")
        # print()




# # Load the JSON files
# json1 = load_json('gauntlet_old.json')
# json2 = load_json('gauntlet.json')
#
# # Compare the JSON files
# differences = compare_cards(json1, json2)
#
# # Print the differences
# print_differences(differences)


gauntlet = load_json('gauntlet.json')['cards']

# for item in gauntlet:
#     card_data = get_card_entry(item['name'])
#     if 'Land' in card_data['type_line'] and len(card_data['color_identity']) == 3:
#         print(item['quantity'], item['name'])


def build_decks(file_path):
    decks = []
    deck_object_list = []
    with open(file_path, 'r') as file:
        current_deck = []
        for line in file:
            line = line.strip()
            if not line:
                decks.append(current_deck)
                current_deck = []
            else:
                current_deck.append(line)
    for deck_list in decks:
        d = deck(deck_list)
        print(d)
        deck_object_list.append(d)
    return deck_object_list

###########################################################################

# build_deck_list("deck.txt", "5c Legends")

# # Save the deck list to a JSON file named 'example_deck.json'
# save_deck_to_json(deck_list, 'example_deck.json')

# Boros Convoke
# Gruul Aggro
# Azorius Control
# 5c Legends
# Temur Analyst
# Dimir Midrange
# Domain
# Gruul Ramp
# Golgari Midrange
# Esper Midrange
# Bant Toxic
# Mono Red Aggro
# Simic Artifacts