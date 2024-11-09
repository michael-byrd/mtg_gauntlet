# from PIL import Image, ImageDraw, ImageFont
# import requests
# from io import BytesIO
#
# def add_number_to_image(image_url, number, position=(372, 960), font_size=72, font_color=(255, 255, 255), circle_color=(0, 0, 0)):
#     # Fetch the image from the URL
#     image = requests.get(image_url).content
#     with open('image.png', 'wb') as f:
#         f.write(image)
#     image = Image.open('image.png').convert('RGBA')
#
#     # Initialize the drawing context
#     draw = ImageDraw.Draw(image)
#     font_path = "/Users/michael-mbp/Downloads/Roboto/Roboto-Bold.ttf"
#     font = ImageFont.truetype(font_path, font_size)
#
#     # Get the size of the number text
#     text_bbox = draw.textbbox((0, 0), str(number), font=font)
#     text_width = text_bbox[2] - text_bbox[0]
#     text_height = text_bbox[3] - text_bbox[1]
#
#     # Calculate circle dimensions
#     circle_radius = max(text_width, text_height) // 2 + 10
#     circle_x1 = position[0] - circle_radius
#     circle_y1 = position[1] - circle_radius + 15
#     circle_x2 = position[0] + circle_radius
#     circle_y2 = position[1] + circle_radius + 15
#
#     # Draw the circle
#     draw.ellipse([(circle_x1, circle_y1), (circle_x2, circle_y2)], fill=circle_color)
#
#     # Calculate text position to be centered in the circle
#     text_x = position[0] - text_width // 2
#     text_y = position[1] - text_height // 2
#
#     # Add the number to the image
#     draw.text((text_x, text_y), str(number), fill=font_color, font=font)
#
#     return image
#
# # Example usage:
# image_url = 'https://cards.scryfall.io/png/front/5/4/54a702cd-ca49-4570-b47e-8b090452a3c3.png?1675957271'  # Example URL
# number = 20
#
# image_with_number = add_number_to_image(image_url, number)
# image_with_number.show()  # Display the image
