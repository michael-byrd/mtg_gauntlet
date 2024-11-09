import json
import requests
import time
import pprint
import os
import glob

current_dir = os.path.dirname(os.path.abspath(__file__))
deck_list_path = os.path.join(current_dir, 'deck_lists')

with open('oracle-cards-20241109220318.json', 'r', encoding="utf8") as f:
    ORACLE_DATA = json.load(f)

ALL_KEYWORDS = set()
for item in ORACLE_DATA:
    for keyword in item['keywords']:
        ALL_KEYWORDS.add(keyword)

def get_card_entry(card_name, delay=0.15):
    """
    Retrieves card details from local Oracle data o`````````````````````````````r, if not found, from the Scryfall API.

    Args:
        card_name (str): The name of the card to look up.
        delay (float, optional): Time to delay between requests to prevent API rate limiting.`

    Returns:
        dict or None: Card details as a dictionary if found, or None if not found or an error occurs.
    """
    # Normalize the card name for comparison
    card_name_lower = card_name.lower()

    # Check if card is in the local data first
    for card in ORACLE_DATA:
        if card['name'].lower() == card_name_lower and card['set_type'] != "funny" and card['layout'] != "token":
            return card

    # Add a delay to prevent rate limiting
    print("Used Scryfall API")
    time.sleep(delay)

    # Query the Scryfall API for the card using fuzzy search
    url = f'https://api.scryfall.com/cards/named?fuzzy={card_name}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching card data: {e}")
        return None  # Handle errors by returning None or an appropriate response


# Consider reworking, using a different approach
# Determine which functions depend on this and see
# if we can find an alternative
def get_oracle_name(card_name):
    url = 'https://api.scryfall.com/cards/named?fuzzy=' + card_name
    # Wait for 100ms to avoid rate limiting
    time.sleep(0.2)
    response = requests.get(url)
    data = response.json()
    # print(card_name, data)
    return data['name']


def get_card_colors(card_name):
    """
    Retrieves the color identity of a Magic: The Gathering card, considering various card layouts.

    Args:
        card_name (str): The name of the card whose colors are to be retrieved.

    Returns:
        list: A list of the card's colors or color identity.
    """
    card = get_card_entry(card_name)
    layout = card['layout']

    if layout in ["adventure", "prototype"]:
        return card['color_identity']
    elif layout == "transform":
        return card['card_faces'][0]['colors']
    elif layout == "modal_dfc":
        colors = {color for face in card['card_faces'] for color in face['colors']}
        return list(colors)
    else:
        return card['colors']


def load_preferred_card_art(file_path='preferred_art.txt'):
    """
    Loads the preferred card art from a text file into a dictionary.

    Args:
        file_path (str): Path to the text file containing preferred card art.
                         Defaults to 'preferred_art.txt'.

    Returns:
        dict: A dictionary mapping card names to their preferred art.
    """
    preferred_card_art = {}

    with open(file_path, 'r') as f:
        preferred_art = f.read().splitlines()
        for item in preferred_art:
            # Ensure correct parsing by handling potential issues with split
            if ',' in item:
                card_name, card_art = item.split(',', 1)
                preferred_card_art[card_name.strip()] = card_art.strip()

    return preferred_card_art


preferred_card_art = load_preferred_card_art()


def get_card_image(card_name, quality='normal'):
    """
    Retrieves the URL for the card image based on the card's name and preferred art.

    Args:
        card_name (str): The name of the card.

    Returns:
        str: The URL of the card image.
    """
    card = get_card_entry(card_name)
    layout = card.get('layout', '')

    # Comment this out since it uses png. We are using normal for now.
    # Check if preferred art is available
    # if card_name in preferred_card_art:
    #     return preferred_card_art[card_name]

    # Determine the image URL based on card layout
    if layout in ['transform', 'modal_dfc', 'flip']:
        return card['card_faces'][0]['image_uris'][quality]

    return card['image_uris'][quality]


def get_main_card_type(type_line):
    """
    Determines the main card type based on the type line.

    Args:
        type_line (str): The type line of the card.

    Returns:
        str: The main card type.
    """
    card_types = [
        "Creature",
        "Artifact",
        "Enchantment",
        "Instant",
        "Sorcery",
        "Planeswalker",
        "Battle",
        "Land",
    ]

    for card_type in card_types:
        if card_type in type_line:
            return card_type

    return "Other"


def sort_cards_by_type(card_list):
    """
    Sorts a list of Magic: The Gathering cards by their card type, based on a predefined order.

    Args:
        card_list (list): A list of cards where each card is represented as a tuple or list,
                          with the card type as the third element (index 2).

    Returns:
        list: A sorted list of cards, ordered by their card type.
    """
    # Define the sorting order for card types
    type_sort_order = {
        "Creature": 1,
        "Planeswalker": 2,
        "Artifact": 3,
        "Enchantment": 4,
        "Instant": 5,
        "Sorcery": 6,
        "Land": 7
    }

    # Sort cards based on the card type using the predefined order; default to infinity for unknown types
    return sorted(card_list, key=lambda card: type_sort_order.get(card[2], float('inf')))


def sort_cards_by_type_and_color(card_list):
    """
    Sorts a list of Magic: The Gathering cards by their card type and then by their color,
    using predefined sorting orders for both type and color.

    Args:
        card_list (list): A list of cards where each card is represented as a tuple or list,
                          with the card type as the third element (index 2) and colors as the fourth (index 3).

    Returns:
        list: A sorted list of cards, ordered first by type and then by color.
    """
    # Define the sorting order for card types
    type_sort_order = {
        "Creature": 1,
        "Instant": 2,
        "Sorcery": 3,
        "Artifact": 4,
        "Enchantment": 5,
        "Planeswalker": 6,
        "Land": 7
    }

    # Define the sorting order for card colors
    color_sort_order = {
        "W": 1,
        "U": 2,
        "B": 3,
        "R": 4,
        "G": 5,
        "Gold": 6,
        "Colorless": 7
    }

    # Helper function to determine color category
    def determine_color_category(colors):
        if len(colors) > 1:
            return "Gold"
        elif len(colors) == 0:
            return "Colorless"
        else:
            return colors[0]
    # Sort cards first by type, then by color category
    return sorted(card_list, key=lambda card: (
        type_sort_order.get(card[2], float('inf')),  # Sort by card type
        color_sort_order.get(determine_color_category(card[3]), float('inf')),  # Sort by card color
        card[0] # Sort by card name
    ))


def collect_and_sort_cards(deck, sideboard):
    all_cards = []

    # Collect and sort cards from the deck
    for key, value in deck.items():
        card = get_card_entry(key)
        card_type = get_main_card_type(card['type_line'])
        card_colors = get_card_colors(key)
        all_cards.append((key, value, card_type, card_colors))

    # Sort the collected deck cards by card type
    all_cards = sort_cards_by_type_and_color(all_cards)

    # TODO: Fix Sideboard
    # Collect cards from the sideboard
    # for key, value in sideboard.items():
    #     card = get_card_entry(key)
    #     card_type = get_main_card_type(card['type_line'])
    #     all_cards.append((key, value, card_type))

    return all_cards


def get_deck_colors(deck):
    color_order = ['W', 'U', 'B', 'R', 'G']
    deck_colors = set()
    for card_name, quantity in deck.items():
        colors = get_card_colors(card_name)
        deck_colors.update(colors)
    deck_colors = list(deck_colors)
    deck_colors.sort(key=lambda x: color_order.index(x))
    return deck_colors

def get_card_type(card):
    if card['layout'] == 'transform':
        return card['card_faces'][0]['type_line']
    return card['type_line']

def separate_card_types(card_dict):
    card_types = {'Creatures': {},
                  'Artifacts': {},
                  'Enchantments': {},
                  'Battles': {},
                  'Spells': {},
                  'Planeswalkers': {},
                  'Lands': {}}
    for card_name, quantity in card_dict.items():
        card = get_card_entry(card_name)
        card_type = get_main_card_type(get_card_type(card))
        if card_type == 'Creature':
            card_types['Creatures'][card_name] = quantity
        elif card_type == 'Artifact':
            card_types['Artifacts'][card_name] = quantity
        elif card_type == 'Enchantment':
            card_types['Enchantments'][card_name] = quantity
        elif card_type == 'Instant' or card_type == 'Sorcery':
            card_types['Spells'][card_name] = quantity
        elif card_type == 'Planeswalker':
            card_types['Planeswalkers'][card_name] = quantity
        elif card_type == 'Land':
            card_types['Lands'][card_name] = quantity
        else:
            card_types['Battles'][card_name] = quantity
    return card_types

def deck_to_html(deck):
    def generate_card_html(quantity, card_name, img_url):
        card = get_card_entry(card_name)
        if card['layout'] == 'split':
            html = f'<li><span class="rotated-card">{quantity} {card_name} <img src="{img_url}" alt="{card_name}"> </span></li>'
            return html
        if card['layout'] == 'transform':
            img_url_front = img_url
            img_url_back = img_url.replace('front', 'back')
            html = f'<li><span class="card">{quantity} {card_name} <img src="{img_url_front}" alt="{card_name}" class="front"> <img src="{img_url_back}" alt="{card_name}" class="back"> </span></li>'
            return html
        html = f'<li><span class="card">{quantity} {card_name} <img src="{img_url}" alt="{card_name}"> </span></li>'
        return html

    for version in deck.mainboard.keys():
        deck_name = deck.deck_name.replace(' ', '_')
        author_name = deck.deck_author.replace(' ', '_')
        event_name = deck.deck_event.replace(' ', '_')
        if author_name == "" and event_name == "":
            deck_name += '_' + version
        else:
            deck_name += '_' + author_name + '_' + event_name
        version_number = version[-1]
        print("<div class=\"deck-container\">")
        print("\t<div class=\"deck-header\">")
        # if len(deck.mainboard.keys()) > 1:
        #     print(f"\t\t<h1>{deck.deck_name} Version {version_number}</h1>")
        # else:
        #     print(f"\t\t<h1>{deck.deck_name}</h1>")
        print(f"\t\tFormat: Standard")
        print(f"\t\t<br>")
        print(f"\t\tSource: Unknown")
        print(f"\t\t<br>")
        print(f"\t\t<button type=\"button\" onclick=\"closeDeckImg('{deck_name}')\" id=\"closeBtn_{deck_name}\" class=\"closeBtn\">")
        print("\t\t\tClose Image")
        print("\t\t</button>")
        print(f"\t\t<img class=\"deck-image-popup\" id=\"deckImg_{deck_name}\" style=\"width: 75%; margin: 0 auto;\" src=\"assets/mtg_decks/{deck_name}.png\" alt=\"Deck Image\">")
        print(f"\t\t<button type=\"button\" onclick=\"showDeckImg('{deck_name}')\" id=\"viewBtn_{deck_name}\">")
        print("\t\t\tView Image")
        print("\t\t</button>")
        print("\t</div>")
        print(f"\t<div class=\"deck-list\">")
        print("\t\t<div class=\"section\">")
        split_deck = separate_card_types(deck.mainboard[version])
        for card_type, cards in split_deck.items():
            if cards and card_type != 'Lands':
                total_cards = sum(cards.values())
                print(f"\t\t\t<h2>{card_type} ({total_cards})</h2>")
                print("\t\t\t<ul>")
                for card_name, quantity in cards.items():
                    print("\t\t\t\t", generate_card_html(quantity, card_name, get_card_image(card_name, 'large')))
                print("\t\t\t</ul>")
        print("\t\t</div>")
        print("\t\t<div class=\"section\">")
        total_cards = sum(split_deck['Lands'].values())
        print(f"\t\t\t<h2>Lands ({total_cards})</h2>")
        print("\t\t\t<ul>")
        for card_name, quantity in split_deck['Lands'].items():
            card = get_card_entry(card_name)
            print("\t\t\t\t", generate_card_html(quantity, card_name, get_card_image(card_name, 'large')))
        print("\t\t\t</ul>")
        print("\t\t</div>")
        print("\t</div>")
        print("</div>")

