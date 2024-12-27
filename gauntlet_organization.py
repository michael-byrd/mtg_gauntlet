from mtg_tools import *
import json
from visualization_tools import *

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


gauntlet = load_json('gauntlet.json')

gauntlet_cards = {}

for card in gauntlet['cards']:
    gauntlet_cards[card['name']] = card['quantity']

cards = {}
for card in gauntlet_cards.keys():
    color = get_card_colors(card)
    card_type = get_main_card_type(get_card_type(card))
    # print(f"{card} ({color}) - {get_main_card_type(card_type)} - {gauntlet_cards[card]}")
    if card_type == "Enchantment":
        card_entry = get_card_entry(card)
        colorID = card_entry['color_identity']
        if len(colorID) == 0:
            cards[card] = gauntlet_cards[card]



collect_and_sort_cards(cards, {})
visual_spoiler_v2(cards, {}, "Gauntlet", "v1", None, "gauntlet")