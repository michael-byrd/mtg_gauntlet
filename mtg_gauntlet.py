import glob
from gauntlet_tools import *
from visualization_tools import *
import hashlib

current_dir = os.path.dirname(os.path.abspath(__file__))
deck_list_path = os.path.join(current_dir, 'deck_lists')
pre_gauntlet_deck_list_oath = os.path.join(current_dir, 'pre_gauntlet_deck_lists')
image_path = os.path.join(current_dir, 'deck_images')


# Ensure the cache directory exists
def ensure_cache_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Before creating the object, compute the hash of the raw_deck
def create_or_load_deck(raw_deck):
    # Ensure the deck_cache directory exists
    cache_directory = 'deck_cache'
    ensure_cache_directory(cache_directory)

    # Calculate the hash for the raw_deck before creating the object
    deck_hash = hashlib.md5(str(raw_deck).encode()).hexdigest()
    cache_file = os.path.join(cache_directory, f'deck_cache_{deck_hash}.pkl')

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

def build_deck_lists(which_decks='gauntlet'):
    print("Building Deck Lists")
    if which_decks == 'gauntlet':
        txt_files = glob.glob(os.path.join(deck_list_path, '*.txt'))
    else:
        txt_files = glob.glob(os.path.join(pre_gauntlet_deck_list_oath, '*.txt'))
    decks = []
    deck_names = []
    for txt_file in txt_files:
        with open(txt_file, 'r') as file:
            current_deck = file.readlines()
            deck_names.append(current_deck[0].strip())
        d = create_or_load_deck(current_deck)
        decks.append(d)
        print(current_deck[0].strip(), "Build")
    return decks

def update_deck_visuals(deck_lists):
    for deck in deck_lists:
        for version in deck.mainboard.keys():
            deck_list = deck.mainboard[version]
            sideboard_list = deck.sideboard[version]
            deck_name = deck.deck_name + " " + version
            visual_spoiler_v2(deck_list, sideboard_list, deck_name, version, deck)
            print(deck_name, version, "Visual done")

if __name__ == "__main__":

    deck_lists = build_deck_lists('gauntlet')

    update_deck_visuals(deck_lists)

    # (deck, sideboard, deck_name, version_number="v1", deck_obj=None):
    # for new_deck in new_decks:
    #     visual_spoiler_v2(new_deck.mainboard['v1'], new_deck.sideboard['v1'], new_deck.deck_name, "v1", new_deck)

    # build_gauntlet(deck_lists, 'gauntlet.json')
    # # Load the JSO≤N files
    # json1 = load_json('gauntlet_old.json')
    # json2 = load_json('gauntlet.json')
    #
    # # Compare the JSON files
    # differences = compare_cards(json1, json2)
    #
    # # Print the differences
    # print_differences(differences)



    exit()

    deck_lists = build_deck_lists()

    for index, deck in enumerate(deck_lists):
        print(index, deck.deck_name)

    duskmourn_decks = ['Azorius Auras', 'Boros Meme Convoke', 'Boros Triggers', 'Delirium Aggro', 'Dimir Skeletons',
                       'Jeskai Rooms', 'Jund Conquest', 'Orzhov Reanimator', 'Rakdos Half-Life', 'Rakdos Sacrifice',
                       '5c Leyline of Mutation', '4c Domain Duskmourn']

    nums = []
    for deck_name in duskmourn_decks:
        for index, deck in enumerate(deck_lists):
            if deck_name in deck.deck_name:
                nums.append(index)


    decks_wanted = [deck_lists[num] for num in nums]

    # build_gauntlet(decks_wanted, 'duskmourn_mini_gauntlet.json')

    # Load the JSON files
    json1 = load_json('duskmourn_mini_gauntlet_old.json')
    json2 = load_json('duskmourn_mini_gauntlet.json')

    # Compare the JSON files
    differences = compare_cards(json1, json2)
    differences_dict = differences_to_dict(differences)

    visual_spoiler_v2(differences_dict, {}, "Duskmourn Mini Gauntlet Update", "")
    # Print the differences
    # print_differences(differences)

    # cards_needed = {}
    #
    # for deck in decks_wanted:
    #     cards_needed_for_deck = {}
    #     for version in deck.mainboard:
    #         for card_name, quantity in deck.mainboard[version].items():
    #             if card_name in cards_needed_for_deck:
    #                 cards_needed_for_deck[card_name] = max(cards_needed_for_deck[card_name], quantity)
    #             else:
    #                 cards_needed_for_deck[card_name] = quantity
    #     for card_name, quantity in cards_needed_for_deck.items():
    #         if card_name in cards_needed:
    #             cards_needed[card_name].append(quantity)
    #         else:
    #             cards_needed[card_name] = [quantity]
    #
    # for card_name in cards_needed:
    #     cards_needed[card_name] = sorted(cards_needed[card_name], reverse=True)
    #
    # for card_name in cards_needed:
    #     cards_needed[card_name] = sum(cards_needed[card_name][:2])
    #
    # print(cards_needed)

    exit()

    build_gauntlet(deck_lists)

    # Load the JSON files
    json1 = load_json('gauntlet_old.json')
    json2 = load_json('gauntlet.json')

    # Compare the JSON files
    differences = compare_cards(json1, json2)

    # Print the differences
    print_differences(differences)



    # with open('deck.txt', 'r') as file:
    #     deck = file.readlines()
    #
    # deck = MTGDeck(deck)
    # visual_spoiler_v2(deck.mainboard['v1'], deck.sideboard['v1'], deck.deck_name)
    #


    def generate_card_html(card_name, img_url):
        html = f'<li><span class="card">{card_name} <img src="{img_url}" alt="{card_name}"> </span></li>'
        return html



    # print(generate_card_html(card['name'], card['image_uris']['normal']))


    # for item in deck_lists:
    #     deck_to_html(item)

    deck = deck_lists[1]
    keywords = set()

    import re

    def is_word_in_string(word, string):
        # Use \b to denote word boundaries, with re.IGNORECASE for case-insensitivity
        pattern = r'\b' + re.escape(word) + r'\b'
        return bool(re.search(pattern, string, re.IGNORECASE))

    def get_all_oracle_text(card_name):
        card = get_card_entry(card_name)
        if 'oracle_text' in card:
            return card['oracle_text']
        elif 'card_faces' in card:
            return card['card_faces'][0]['oracle_text'] + " // " + card['card_faces'][1]['oracle_text']

    def get_deck_keywords(deck):
        deck_keywords = set()
        # Compile a single regex pattern for all keywords
        sorted_keywords = sorted(ALL_KEYWORDS, key=len, reverse=True)
        keyword_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(keyword) for keyword in sorted_keywords) + r')\b',
                                     re.IGNORECASE)

        for version in deck.mainboard:
            for card in deck.mainboard[version]:
                oracle_text = get_all_oracle_text(card)

                matches = keyword_pattern.findall(oracle_text)
                deck_keywords.update(matches)
        return deck_keywords



    # deck = deck_lists[2]
    #
    # for item in deck.mainboard['v1']:
    #     card = get_card_entry(item)
    #     if 'all_parts' in card:
    #         for part in card['all_parts']:
    #             if part['component'] == 'token':
    #                 print(part)

    # for i ,deck in enumerate(deck_lists):
    #     print(deck.deck_name, deck.mainboard['v1'])






    nums = [1, 6, 8, 10, 13, 19, 20, 25, 26, 28]
    decks_wanted = [deck_lists[num] for num in nums]

    cards_needed = {}

    for deck in decks_wanted:
        cards_needed_for_deck = {}
        for version in deck.mainboard:
            for card_name, quantity in deck.mainboard[version].items():
                if card_name in cards_needed_for_deck:
                    cards_needed_for_deck[card_name] = max(cards_needed_for_deck[card_name], quantity)
                else:
                    cards_needed_for_deck[card_name] = quantity
        for card_name, quantity in cards_needed_for_deck.items():
            if card_name in cards_needed:
                cards_needed[card_name].append(quantity)
            else:
                cards_needed[card_name] = [quantity]

    for card_name in cards_needed:
        cards_needed[card_name] = sorted(cards_needed[card_name], reverse=True)

    for card_name in cards_needed:
        cards_needed[card_name] = sum(cards_needed[card_name][:2])

    all_keywords_needed = set()
    for deck in decks_wanted:
        deck_kw = get_deck_keywords(deck)
        # lower case all of them
        deck_kw = [keyword.lower() for keyword in deck_kw]
        all_keywords_needed.update(deck_kw)

    # Title case all_keywords_needed
    # all_keywords_needed = sorted([keyword.title() for keyword in all_keywords_needed])
    # print(all_keywords_needed)



    # visual_spoiler_v2(cards_needed, {}, "Duskmourn Mini Gauntlet", "")




    # print(sorted(ALL_KEYWORDS))
    # begin = time.time()
    # for deck in deck_lists:
    #     kw = sorted(get_deck_keywords(deck))
    #     kw = [keyword.title() for keyword in kw]
    #     print(deck.deck_name, kw)
    # print(time.time() - begin)



    # split_deck = separate_card_types(deck_lists[5].mainboard['v1'])
    # for card_type in split_deck:
    #     print(card_type, split_deck[card_type])

    # for item in deck_lists[5].mainboard['v1']:
    #     card = get_card_entry(item)
    #     # Add equal spacing between the two pieces of data
    #
    #     print(f"{card['name']:<40} {get_main_card_type(get_card_type(card))}")
        # card_text = f'{deck_lists[5].mainboard["v1"][item]} &ensp; {item}'
        # print(generate_card_html(card_text, card['image_uris']['large']))



    # print("\n \n")
    # print("Deck Objects Built \n \n")
    # update_deck_visuals(deck_lists)

    # images = glob.glob(os.path.join(image_path, '*.png'))
    # images = sorted(images)
    # for image_file in images:
    #     print(f"<img src=\"/assets/images/magic_visuals/{image_file.split('/')[-1]}\">")

    # # Read in deck.txt
    # with open('deck.txt', 'r') as file:
    #     deck = file.readlines()
    # #
    # deck = MTGDeck(deck)
    # visual_spoiler_v2(deck.mainboard['v1'], deck.sideboard['v1'], deck.deck_name)


