import tkinter as tk
from tkinter import messagebox
from mtg_gauntlet import build_deck_lists  # Import the function
import os

# Ensure that current working directory paths are set
current_dir = os.path.dirname(os.path.abspath(__file__))
deck_list_path = os.path.join(current_dir, 'deck_lists')
pre_gauntlet_deck_list_oath = os.path.join(current_dir, 'pre_gauntlet_deck_lists')
image_path = os.path.join(current_dir, 'deck_images')

# Initialize the main window
root = tk.Tk()
root.title("Magic Gauntlet Deck Viewer")
root.geometry("800x600")  # Adjust the size as needed

# Load the decks using build_deck_lists
try:
    decks = build_deck_lists('gauntlet')  # Assuming this function returns a list of MTGDeck objects
except Exception as e:
    messagebox.showerror("Error", f"Failed to load decks: {e}")
    root.quit()

# Check if there are any decks
if not decks:
    messagebox.showerror("Error", "No decks found.")
    root.quit()

# Frame for displaying deck info
frame = tk.Frame(root)
frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

# Create a Listbox to display deck names
listbox = tk.Listbox(frame, height=15, width=50)
listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create a scrollbar for the Listbox
scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

# Link the scrollbar with the Listbox
listbox.config(yscrollcommand=scrollbar.set)

# Create a frame to hold the deck details, which will be displayed to the right of the listbox
details_frame = tk.Frame(root)
details_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

# Create a label to display the selected deck's details
details_label = tk.Label(details_frame, text="Select a deck to view details", justify="left", anchor="nw", font=('Helvetica', 10))
details_label.pack(pady=20, fill="both", expand=True)

decks = sorted(decks, key=lambda x: x.deck_name)

# Populate the Listbox with deck names
for deck in decks:
    listbox.insert(tk.END, deck.deck_name)  # Assuming each deck object has a 'deck_name' attribute


# Function to update deck details when a deck is selected
def show_deck_details(event=None):
    selected_index = listbox.curselection()  # Get selected index
    if selected_index:
        current_deck_index = selected_index[0]
        deck = decks[current_deck_index]

        # Display deck details (general information)
        deck_info = f"Deck Name: {deck.deck_name}\n"
        deck_info += f"Author: {deck.deck_author}\n"
        deck_info += f"Event: {deck.deck_event}\n\n"

        for version in deck.mainboard.keys():
            deck_info += f"Version {version}:\n"
            deck_info += "Mainboard Cards:\n"
            for card, count in deck.mainboard[version].items():  # Assuming deck.mainboard is a dictionary with card names and counts
                deck_info += f"{card}: {count}\n"

            deck_info += "\nSideboard Cards:\n"
            for card, count in deck.sideboard[version].items():  # Assuming deck.sideboard is a dictionary with card names and counts
                deck_info += f"{card}: {count}\n"
            deck_info += "\n"
        details_label.config(text=deck_info)  # Update the label with the deck's information

# Bind the Listbox selection event to show the selected deck's details
listbox.bind('<<ListboxSelect>>', show_deck_details)

# Configure grid weights to allow resizing
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)

# Start the Tkinter event loop
root.mainloop()