import requests

# Set ID for the Base Set 1
set_id = 'base1'
url = f'https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}'

# Fetch cards
response = requests.get(url)
if response.status_code == 200:
    cards = response.json().get('data', [])
    print(f"Cards in the set '{set_id}':")
    for card in cards:
        name = card['name']
        card_id = card['id']
        image_url = card['images']['large']  # You can also use 'small' for a smaller image
        print(f"{name} (ID: {card_id}) - Image URL: {image_url}")
else:
    print(f"Failed to retrieve cards: {response.status_code} - {response.text}")