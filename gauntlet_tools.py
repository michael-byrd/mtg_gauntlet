from mtg_tools import *
from mtg_deck import MTGDeck

def save_deck_to_json(deck, filename):
    with open(filename, 'w') as file:
        json.dump(deck, file, indent=4)

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def build_gauntlet(list_of_decks, filename='gauntlet.json'):
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

    save_deck_to_json(gauntlet_list, filename)

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


def differences_to_dict(differences):
    if not differences:
        return {}

    diff_dict = {}
    for diff in differences:
        diff_dict[diff['name']] = diff['quantity_in_file2'] - diff['quantity_in_file1']
    return diff_dict