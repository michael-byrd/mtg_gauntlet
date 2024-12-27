from mtg_tools import *
import pickle
import hashlib

class MTGDeck:
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
                name, number = card_name, quantity + self.sideboard.get(version, {}).get(card_name, 0)
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
            legalities = card['legalities']
            for format, legality in legalities.items():
                if legality == 'legal':
                    card_legal_formats.add(format)
            legal_formats = legal_formats.intersection(card_legal_formats) if legal_formats else card_legal_formats
        return legal_formats

    def is_standard_legal(self, version="v1"):
        return 'standard' in self.legal_formats(version)