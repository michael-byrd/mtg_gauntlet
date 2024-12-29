import hashlib
import os
import pickle

from mtg_tools import get_card_colors, get_card_entry, get_oracle_name


class MTGDeck:
    """
    A class representing a Magic: The Gathering (MTG) deck.

    The MTGDeck class is designed to parse, manage, and perform operations on
    an MTG deck, including its mainboard and sideboard, as well as associated
    metadata such as deck name, author, and event details.
    It can load and save deck data from/to cache and calculate
    the deck's hash for consistency checking.

    Attributes:
        mainboard (dict): A dictionary storing the mainboard of the deck, keyed by version.
        sideboard (dict): A dictionary storing the sideboard of the deck, keyed by version.
        deck_name (dict): A dictionary storing the deck's name(s), keyed by version.
        deck_author (dict): A dictionary storing the deck's author(s), keyed by version.
        deck_event (dict): A dictionary storing the event(s) associated with the deck, keyed by version.
        raw_deck (list): A list representing the raw input deck data to be parsed.

    Methods:
        __init__(raw_deck):
            Initializes the MTGDeck object with the provided raw deck data and builds the deck list.

        _calculate_hash():
            Generates an MD5 hash from the raw deck data for consistency checking.

        load_from_cache(cache_file):
            Loads and returns a cached MTGDeck object from the specified cache file if it exists.

        save_to_cache(cache_file):
            Saves the current MTGDeck object to the specified cache file.

        build_deck_list():
            Parses the raw deck data, extracting the metadata (name, author, event)
            and splitting the deck into mainboard and sideboard for each version.

        get_cards_needed():
            Returns a dictionary of cards needed across all versions of the deck, considering both mainboard
            and sideboard quantities.

        get_color_distribution():
            Analyzes the deck's mainboard to return a distribution of card colors.

        legal_formats(version="v1"):
            Returns a set of legal formats for the given deck version based on the legalities of each card in
            the mainboard.

        is_standard_legal(version="v1"):
            Returns True if the deck is legal in the Standard format for the given version, otherwise False.
    """

    def __init__(self, raw_deck):
        self.mainboard = {}
        self.sideboard = {}
        self.deck_name = {}
        self.deck_author = {}
        self.deck_event = {}
        self.raw_deck = raw_deck
        self.build_deck_list()

    def _calculate_hash(self):
        # Create a hash from the raw_deck variable
        return hashlib.md5(str(self.raw_deck).encode()).hexdigest()

    @staticmethod
    def load_from_cache(cache_file):
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        return None

    def save_to_cache(self, cache_file):
        with open(cache_file, "wb") as f:
            pickle.dump(self, f)

    def build_meta_info(self, meta_info):
        meta_info_dict = {}
        meta_info = [x.strip() for x in meta_info.split("\n") if x.strip()]
        if len(meta_info) == 1:
            meta_info_dict["Name"] = (
                meta_info[0].strip().removeprefix("# ").removeprefix("Name: ")
            )
        else:
            for meta in meta_info:
                key, value = meta.split(":")
                meta_info_dict[key.strip()] = value.strip()

        if "Name" in meta_info_dict:
            names = meta_info_dict["Name"].split(", ")
            for i, item in enumerate(names):
                self.deck_name["v" + str(i + 1)] = item.strip()
        if "Author" in meta_info_dict:
            authors = meta_info_dict["Author"].split(", ")
            for i, item in enumerate(authors):
                self.deck_author["v" + str(i + 1)] = item.strip()
        if "Event" in meta_info_dict:
            events = meta_info_dict["Event"].split(", ")
            for i, item in enumerate(events):
                self.deck_event["v" + str(i + 1)] = item.strip()

    def build_deck_list(self):
        content = "".join(self.raw_deck)
        sections = content.split("# v")
        self.build_meta_info(sections.pop(0))

        versions = {}
        for section in sections:
            if section.strip():
                version, cards = section.split("\n", 1)
                versions[f"v{version.strip()}"] = cards.strip().split("\n")

        for version, cards in versions.items():
            version_mainboard = {}
            version_sideboard = {}
            if "# Sideboard" in cards:
                main_raw_deck = cards[: cards.index("# Sideboard")]
                sideboard_raw_deck = cards[cards.index("# Sideboard") + 1 :]
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
                name, number = card_name, quantity + self.sideboard.get(
                    version, {}
                ).get(card_name, 0)
                if name in cards_needed:
                    cards_needed[name] = max(cards_needed[name], number)
                else:
                    cards_needed[name] = number
            for card_name, quantity in self.sideboard[version].items():
                name, number = card_name, quantity
                if name in cards_needed:
                    cards_needed[name] = max(cards_needed[name], number)
                else:
                    cards_needed[name] = number
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

    def legal_formats(self, version="v1"):
        legal_formats = set()
        for card_name in self.mainboard[version]:
            card_legal_formats = set()
            card = get_card_entry(card_name)
            legalities = card["legalities"]
            for format, legality in legalities.items():
                if legality == "legal":
                    card_legal_formats.add(format)
            legal_formats = (
                legal_formats.intersection(card_legal_formats)
                if legal_formats
                else card_legal_formats
            )
        return legal_formats

    def is_standard_legal(self, version="v1"):
        return "standard" in self.legal_formats(version)
