# Read the content of the file
with open('multi_version_deck.txt', 'r') as file:
    lines = file.readlines()

# Store the deck name
deck_name = lines[0].strip()

# Join the lines back into a single string, ignoring the first line (deck name)
content = ''.join(lines[1:])

# Split the content at the version markers
sections = content.split('# v')
versions = {}

for section in sections:
    if section.strip():
        version, cards = section.split('\n', 1)
        versions[f'v{version.strip()}'] = cards.strip().split('\n')

for version, cards in versions.items():
    print(cards)

# Display the parsed data
# print(f"Deck Name: {deck_name}\n")
# for version, cards in versions.items():
#     print(f"Version {version}:")
#     for card in cards:
#         print(f"  {card}")
#     print()