import math
import time
import json
import requests
import cairosvg
import io
from PIL import Image, ImageDraw, ImageFont
from mtg_tools import *

FONT_PATH = "assets/Beleren-Bold.ttf"


def load_svg_as_image(svg_path):
    png_bytes = cairosvg.svg2png(url=svg_path)
    image = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
    return image


def add_number_to_image(image_url, number, position=(372, 960), font_size=48, font_color=(255, 255, 255),
                        circle_color=(0, 0, 0)):
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


def visual_spoiler_v2(deck, sideboard, deck_name, version_number="v1", deck_obj=None, file_name=None):
    deck_colors = get_deck_colors(deck)
    distinct_num_cards_deck = len(deck)
    distinct_num_cards_sideboard = len(sideboard)
    cards_in_row = 6
    total_rows_needed = math.ceil(distinct_num_cards_deck / cards_in_row)  # Only doing main deck for right now.

    # Define card and layout dimensions
    card_width, card_height = 745, 1040
    card_width, card_height = 488, 680  # Trying normal instead of png

    total_horizontal_width = cards_in_row * card_width
    total_vertical_height = total_rows_needed * card_height
    number_cards_bottom_row = distinct_num_cards_deck % cards_in_row
    bottom_row_width = card_width * number_cards_bottom_row
    bottom_row_white_space = total_horizontal_width - bottom_row_width
    bottom_row_start = bottom_row_white_space // 2

    # create a blank image
    blank_image = Image.new('RGBA', (total_horizontal_width, total_vertical_height))

    # Add deck name at the top
    draw = ImageDraw.Draw(blank_image)
    font_size = 96
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Get text size
    text_bbox = draw.textbbox((0, 0), deck_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (total_horizontal_width - text_width) // 2
    text_y = 10  # Margin from the top

    draw.text((text_x, text_y), deck_name, font=font, fill=(153, 160, 171))  # Black text
    vertical_title_displacement = text_height + text_y + 40

    new_image = Image.new('RGBA', (total_horizontal_width, total_vertical_height + vertical_title_displacement))
    new_image.paste(blank_image, (0, 0))
    blank_image = new_image

    for i, item in enumerate(deck_colors):
        mana_image = load_svg_as_image(f'assets/{item}.svg')
        mana_symbol_size = vertical_title_displacement - 10
        mana_image = mana_image.resize((mana_symbol_size, mana_symbol_size))
        blank_image.paste(mana_image, (5 + (mana_symbol_size + 5) * i, 5), mana_image)

    all_cards = collect_and_sort_cards(deck, sideboard)

    for i, (card_name, quantity, card_type, card_colors) in enumerate(all_cards):
        url = get_card_image(card_name)
        image = add_number_to_image(url, quantity, (card_width // 2, card_height - 50))

        # Determine card position
        on_bottom_row = i >= distinct_num_cards_deck - number_cards_bottom_row
        current_row = i // cards_in_row
        current_column = i % cards_in_row
        if on_bottom_row:
            current_position = (
            bottom_row_start + current_column * card_width, current_row * card_height + vertical_title_displacement)
        else:
            current_position = (current_column * card_width, current_row * card_height + vertical_title_displacement)

        blank_image.paste(image, current_position, image)
        image.close()
    # blank_image.show()
    # replace spaces in deck name with underscores

    if not file_name:
        file_name = ""
        if deck_obj:
            file_name = deck_obj.deck_name.replace(" ", "_") + "_" + deck_obj.deck_author.replace(" ", "_") + "_" + deck_obj.deck_event.replace(" ", "_")
        else:
            file_name = deck_name.replace(" ", "_")

    # Trim all "_" from end
    file_name = file_name.rstrip("_")
    blank_image.save(f"deck_images/{file_name}.png")
