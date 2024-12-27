import json
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor
import glob
from gauntlet_tools import *
from visualization_tools import *
import hashlib

current_dir = os.path.dirname(os.path.abspath(__file__))
deck_list_path = os.path.join(current_dir, 'deck_lists')
pre_gauntlet_deck_list_path = os.path.join(current_dir, 'pre_gauntlet_deck_lists')
image_path = os.path.join(current_dir, 'deck_images')

# Function to load card collection
def load_card_collection(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return {card["name"]: card["quantity"] for card in data["cards"]}

# Check if a combination can be built
def can_build_combination(deck_combination, card_collection):
    combined_cards_needed = {}
    for deck in deck_combination:
        for card_name, quantity in deck.get_cards_needed().items():
            combined_cards_needed[card_name] = combined_cards_needed.get(card_name, 0) + quantity
            # Early termination if we exceed the available cards
            if combined_cards_needed[card_name] > card_collection.get(card_name, 0):
                return False
    return True

# Check if a combination is buildable
def check_combination(combo_and_collection):
    combo, card_collection = combo_and_collection
    return combo if can_build_combination(combo, card_collection) else None

# Generate combinations of size r
def generate_combinations_for_rank(deck_objects, r):
    return list(combinations(deck_objects, r))

# Main function
def find_buildable_combinations_parallel(deck_objects, card_collection_json):
    card_collection = load_card_collection(card_collection_json)
    buildable_combinations = []
    n = len(deck_objects)

    # Parallelize by combination size (r)
    with ProcessPoolExecutor() as executor:
        # Generate combinations for each r in parallel
        all_combinations_by_r = executor.map(
            generate_combinations_for_rank,
            [deck_objects] * n,   # deck_objects as input
            range(9, 10)       # r values
        )

        # Flatten the list of combinations and prepare for evaluation
        all_combinations = [
            (combo, card_collection)
            for combinations_for_r in all_combinations_by_r
            for combo in combinations_for_r
        ]

    print("Total combinations to check:", len(all_combinations))

    # Check combinations in parallel
    with ProcessPoolExecutor() as executor:
        results = executor.map(check_combination, all_combinations)

    for result in results:
        if result:
            buildable_combinations.append(tuple(deck.deck_name for deck in result))

    return buildable_combinations

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
        txt_files = glob.glob(os.path.join(pre_gauntlet_deck_list_path, '*.txt'))
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

# Example Usage
if __name__ == "__main__":
    # Load your decks
    decks = build_deck_lists('gauntlet')

    # Path to card collection JSON file
    card_collection_file = "gauntlet.json"


    for i, deck in enumerate(decks):
        print(i, deck.deck_name)
    small_list = [1, 2, 4, 6, 7, 10, 11, 12, 13, 14, 15, 16, 19, 21, 23, 24, 26, 27, 34, 37]
    decks = [decks[i] for i in small_list]
    # Find combinations of decks you can build
    buildable = find_buildable_combinations_parallel(decks, card_collection_file)

    print("Buildable Deck Combinations:")
    for combo in buildable:
        print(combo)