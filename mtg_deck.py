from mtg_tools import *
import pickle
import hashlib

class MTGDeck:
    def __init__(self, raw_deck):
        self.mainboard = {}
        self.sideboard = {}
        self.deck_name = ""
        self.deck_author = ""
        self.deck_event = ""
        self.raw_deck = raw_deck
        self.build_deck_list()

    def _calculate_hash(self):
        # Create a hash from the raw_deck variable
        return hashlib.md5(str(self.raw_deck).encode()).hexdigest()

    @staticmethod
    def load_from_cache(cache_file):
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None

    def save_to_cache(self, cache_file):
        with open(cache_file, 'wb') as f:
            pickle.dump(self, f)
    def build_deck_list(self):
        meta_info_dict = {}
        # self.deck_name = self.raw_deck[0].strip().removeprefix("# ").removeprefix("Name: ")
        # content = ''.join(self.raw_deck[1:])

        content = ''.join(self.raw_deck)
        sections = content.split('# v')
        meta_info = sections.pop(0)
        meta_info = [x.strip() for x in meta_info.split('\n') if x.strip()]
        if len(meta_info) == 1:
            meta_info_dict["Name"] = meta_info[0].strip().removeprefix("# ").removeprefix("Name: ")
        else:
            for meta in meta_info:
                key, value = meta.split(":")
                meta_info_dict[key.strip()] = value.strip()

        if "Name" in meta_info_dict:
            self.deck_name = meta_info_dict["Name"]
        if "Author" in meta_info_dict:
            self.deck_author = meta_info_dict["Author"]
        if "Event" in meta_info_dict:
            self.deck_event = meta_info_dict["Event"]

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