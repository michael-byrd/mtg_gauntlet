# basic use of scryfall api

import math
import time
import json
import requests
import cairosvg
import io
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "Beleren-Bold.ttf"

with open('oracle-cards-20240723210312.json', 'r', encoding="utf8") as f:
    data = json.load(f)

with open('default-cards-20240901211624.json', 'r', encoding="utf8") as f:
    default_data = json.load(f)

# The name you want to search for
search_name = 'Plains'

# Find all entries with the given name
matching_entries = [entry for entry in default_data if entry.get('name') == search_name]

# Output the matching entries
for entry in matching_entries:
    pass
    # if 'frame_effects' in entry or entry.get('border_color') == "borderless" or entry.get('full_art'):
    #     print(entry.get('set'))
    #     print(entry.get('image_uris').get('png'))

def load_svg_as_image(svg_path):
    png_bytes = cairosvg.svg2png(url=svg_path)
    image = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
    return image

# Inside of mtg_tools.py
def get_card_entry(card_name, delay=0.2):
    # Normalize the card name for comparison
    card_name_lower = card_name.lower()

    # Check if card is in the local data first
    for card in data:
        if card['name'].lower() == card_name_lower and card['set_type'] != "funny":
            return card

    # Add a delay to prevent rate limiting
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

# Inside of mtg_tools.py
def get_card_colors(card_name):
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


def get_card_image(card_name):
    """
    Retrieves the URL for the card image based on the card's name and preferred art.

    Args:
        card_name (str): The name of the card.

    Returns:
        str: The URL of the card image.
    """
    card = get_card_entry(card_name)
    layout = card.get('layout', '')

    # Check if preferred art is available
    if card_name in preferred_card_art:
        return preferred_card_art[card_name]

    # Determine the image URL based on card layout
    if layout in ['transform', 'modal_dfc', 'flip']:
        return card['card_faces'][0]['image_uris']['png']

    return card['image_uris']['png']

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
        "Land",
        "Artifact",
        "Enchantment",
        "Instant",
        "Sorcery",
        "Planeswalker"
    ]

    for card_type in card_types:
        if card_type in type_line:
            return card_type

    return "Other"


# Would like to phase this function out
# since we have the deck class now.
def build_deck_list(file_name):
    """
    Builds dictionaries for deck and sideboard card quantities from a file.

    Args:
        file_name (str): The name of the file containing the card list.

    Returns:
        tuple: Two dictionaries, one for the main deck and one for the sideboard,
               mapping card names to their quantities.
    """
    deck_dict = {}
    sideboard_dict = {}

    with open(file_name, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]  # Remove empty lines and trim whitespace
    name = lines.pop(0).strip('# ')
    # Split the deck and sideboard sections
    if '# Sideboard' in lines:
        sideboard_index = lines.index('# Sideboard')
        deck_lines = lines[:sideboard_index]
        sideboard_lines = lines[sideboard_index + 1:]
    else:
        deck_lines = lines
        sideboard_lines = []

    # Populate deck_dict and sideboard_dict
    for line in deck_lines:
        quantity, card_name = line.split(' ', 1)
        deck_dict[card_name] = int(quantity)

    for line in sideboard_lines:
        quantity, card_name = line.split(' ', 1)
        sideboard_dict[card_name] = int(quantity)
    print(deck_dict, sideboard_dict, name)
    return deck_dict, sideboard_dict, name

# image = requests.get("https://cards.scryfall.io/png/front/5/4/54a702cd-ca49-4570-b47e-8b090452a3c3.png?1675957271").content
# with open('image.jpeg', 'wb') as f:
#     f.write(image)
# image = Image.open('image.jpeg')
# image.show()

def sort_cards_by_type(cards):
    # Define a sorting order for card types
    card_type_order = {
        "Creature": 1,
        "Planeswalker": 2,
        "Artifact": 3,
        "Enchantment": 4,
        "Instant": 5,
        "Sorcery": 6,
        "Land": 7
    }

    # Sort all cards by card type using the predefined order
    return sorted(cards, key=lambda x: card_type_order.get(x[2], float('inf')))

def sort_cards_by_type_and_color(cards):
    # Define a sorting order for card types
    card_type_order = {
        "Creature": 1,
        "Instant": 2,
        "Sorcery": 3,
        "Artifact": 4,
        "Enchantment": 5,
        "Planeswalker": 6,
        "Land": 7
    }

    # Define a sorting order for colors
    color_order = {
        "W": 1,
        "U": 2,
        "B": 3,
        "R": 4,
        "G": 5,
        "Gold": 6,
        "Colorless": 7
    }

    # Function to determine the color category
    def get_color_category(colors):
        if len(colors) > 1:
            return "Gold"
        elif len(colors) == 0:
            return "Colorless"
        else:
            return colors[0]

    # Sort cards first by type, then by color
    return sorted(cards, key=lambda x: (
        card_type_order.get(x[2], float('inf')),  # Sort by card type
        color_order.get(get_color_category(x[3]), float('inf'))  # Sort by card color
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


# Add this in later.
def visual_spoiler_v1():
    deck, sideboard, name = build_deck_list('deck.txt')
    total_card_count = sum(deck.values()) + sum(sideboard.values())
    total_rows_needed = math.ceil(total_card_count / 20)

    card_width, card_height = 745, 1040
    horizontal_buffer = 10
    vertical_buffer = 20
    vertical_delta = 120

    total_horizontal_width = 5 * card_width + 4 * horizontal_buffer
    total_vertical_height = total_rows_needed * (card_height + 3 * vertical_delta) + 2 * vertical_buffer

    for key, value in deck.items():
        # print(key, value)
        get_card_image(key)

    # create a blank image
    blank_image = Image.new('RGBA', (total_horizontal_width, total_vertical_height))

    all_cards = collect_and_sort_cards(deck, sideboard)

    i = 0
    for card_name, quantity, _ in all_cards:
        url = get_card_image(card_name)
        image = requests.get(url).content
        with open('image.png', 'wb') as f:
            f.write(image)
        image = Image.open('image.png').convert('RGBA')

        for _ in range(quantity):
            stack_num = 4 if i < sum(deck.values()) else 3
            current_row = math.floor(i / 20)
            current_column = (i % 20) // stack_num
            current_card = i % stack_num

            x_position = current_column * (card_width + horizontal_buffer)
            y_position = current_row * (
                        card_height + vertical_buffer + 3 * vertical_delta) + current_card * vertical_delta
            position = (x_position, y_position)

            blank_image.paste(image, position, image)
            i += 1

        image.close()
    blank_image.show()
    # blank_image.save("boros_mouse_aggro.png")

# visual_spoiler_v1()
def add_number_to_image(image_url, number, position=(372, 960), font_size=72, font_color=(255, 255, 255), circle_color=(0, 0, 0)):
    # Fetch the image from the URL
    image = requests.get(image_url).content
    with open('image.png', 'wb') as f:
        f.write(image)
    image = Image.open('image.png').convert('RGBA')

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Get the size of the number text
    text_bbox = draw.textbbox((0, 0), str(number), font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate circle dimensions
    circle_radius = max(text_width, text_height) // 2 + 10
    circle_x1 = position[0] - circle_radius
    circle_y1 = position[1] - circle_radius + 15
    circle_x2 = position[0] + circle_radius
    circle_y2 = position[1] + circle_radius + 15

    # Draw the circle
    draw.ellipse([(circle_x1, circle_y1), (circle_x2, circle_y2)], fill=circle_color)

    # Calculate text position to be centered in the circle
    text_x = position[0] - text_width // 2
    text_y = position[1] - text_height // 2

    # Add the number to the image
    draw.text((text_x, text_y), str(number), fill=font_color, font=font)

    return image


def get_deck_colors(deck):
    color_order = ['W', 'U', 'B', 'R', 'G']
    deck_colors = set()
    for card_name, quantity in deck.items():
        colors = get_card_colors(card_name)
        deck_colors.update(colors)
    deck_colors = list(deck_colors)
    deck_colors.sort(key=lambda x: color_order.index(x))
    return deck_colors

def number_cards_per_row(distinct_num_cards_deck):
    if distinct_num_cards_deck > 20:
        return 6
    elif distinct_num_cards_deck == 20:
        return 5
    elif distinct_num_cards_deck % 4 == 0:
        return 4
    elif distinct_num_cards_deck % 5 == 0:
        return 5
    elif distinct_num_cards_deck % 4 < distinct_num_cards_deck % 5:
        return 5
    else:
        return 4



def visual_spoiler_v2(deck, sideboard, deck_name):
    deck_colors = get_deck_colors(deck)
    distinct_num_cards_deck = len(deck)
    distinct_num_cards_sideboard = len(sideboard)
    cards_in_row = number_cards_per_row(distinct_num_cards_deck)
    total_rows_needed = math.ceil(distinct_num_cards_deck/cards_in_row)  # Only doing main deck for right now.

    # Define card and layout dimensions
    card_width, card_height = 745, 1040

    total_horizontal_width = cards_in_row * card_width
    total_vertical_height = total_rows_needed * card_height
    number_cards_bottom_row = distinct_num_cards_deck % cards_in_row
    bottom_row_width = card_width * number_cards_bottom_row
    bottom_row_white_space = total_horizontal_width - bottom_row_width
    bottom_row_start = bottom_row_white_space // 2

    # create a blank image
    blank_image = Image.new('RGBA', (total_horizontal_width, total_vertical_height), (255, 255, 255))

    # Add deck name at the top
    draw = ImageDraw.Draw(blank_image)
    font_size = 144
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Get text size
    text_bbox = draw.textbbox((0, 0), deck_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (total_horizontal_width - text_width) // 2
    text_y = 10  # Margin from the top

    draw.text((text_x, text_y), deck_name, font=font, fill=(0, 0, 0))  # Black text
    vertical_title_displacement = text_height + text_y + 40

    new_image = Image.new('RGBA', (total_horizontal_width, total_vertical_height + vertical_title_displacement), (255, 255, 255))
    new_image.paste(blank_image, (0, 0))
    blank_image = new_image

    for i, item in enumerate(deck_colors):
        mana_image = load_svg_as_image(f'assets/{item}.svg')
        mana_symbol_size = vertical_title_displacement - 10
        mana_image = mana_image.resize((mana_symbol_size, mana_symbol_size))
        blank_image.paste(mana_image, (5 + (mana_symbol_size + 5) * i, 5), mana_image)




    all_cards = collect_and_sort_cards(deck, sideboard)
    print(all_cards)
    for i, (card_name, quantity, card_type, card_colors) in enumerate(all_cards):
        url = get_card_image(card_name)
        image = add_number_to_image(url, quantity)

        # Determine card position
        on_bottom_row = i >= distinct_num_cards_deck - number_cards_bottom_row
        current_row = i // cards_in_row
        current_column = i % cards_in_row
        if on_bottom_row:
            current_position = (bottom_row_start + current_column * card_width, current_row * card_height + vertical_title_displacement)
        else:
            current_position = (current_column * card_width, current_row * card_height + vertical_title_displacement)

        blank_image.paste(image, current_position, image)
        image.close()
    # blank_image.show()
    blank_image.save(f"deck_images/{deck_name}.png")
# deck, sideboard, deck_name = build_deck_list('deck.txt')
# visual_spoiler_v2(deck, sideboard, deck_name)



# Work in progress for card type symbols


# card_types = ['Creature', 'Artifact', 'Enchantment', 'Instant', 'Sorcery', 'Battle', 'Planeswalker', 'Land']
# horizontal_position = 5
# for i, item in enumerate(card_types):
#     symbol_image = load_svg_as_image(f'assets/{item}_symbol.svg')
#     # if item != 'Planeswalker':
#     #     symbol_image = load_svg_as_image(f'assets/{item}_symbol.svg')
#     # else:
#     #     symbol_image = Image.open(f'assets/{item}_symbol.webp')
#
#     # Maximum size for the radius
#     max_diameter = vertical_title_displacement - 10
#
#     # Get the old size of the image
#     old_width, old_height = symbol_image.size
#
#     # Determine the larger dimension (either width or height)
#     largest_dimension = max(old_width, old_height)
#
#     # Calculate the scaling factor to fit within the 50-pixel radius
#     scaling_factor = max_diameter / largest_dimension
#
#     # Calculate the new width and height while maintaining aspect ratio
#     new_width = int(old_width * scaling_factor)
#     new_height = int(old_height * scaling_factor)
#
#     # Resize the image
#     symbol_image = symbol_image.resize((new_width, new_height))
#
#     # Calculate the vertical position to center the image within the 50-pixel space
#     vertical_space = max_diameter - new_height
#     vertical_position = vertical_space // 2
#
#     # Paste the image centered vertically within the available space
#     blank_image.paste(symbol_image, (horizontal_position, vertical_position + 5), symbol_image)
#
#     # Move the horizontal position for the next image
#     horizontal_position += new_width + 5