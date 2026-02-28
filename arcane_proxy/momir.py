import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
import logging
import random
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("momir.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)

def load_random_card():
    """Fetch a random card from Scryfall's API and display it in the window."""
    try:
        logger.info("Starting to fetch a random card from Scryfall API...")
        
        # Fetch a random card from Scryfall's API
        response = requests.get("https://api.scryfall.com/cards/random")
        logger.debug(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch card: HTTP {response.status_code}")
            raise Exception(f"Failed to fetch card: HTTP {response.status_code}")
        
        card_data = response.json()
        print(card_data)
        logger.debug(f"Card data structure: {card_data.keys()}")
        logger.info(card_data.get("card", {}).get("name", {}))
        card_image_url = card_data.get("image_uris", {}).get("normal")
        if not card_image_url:
            logger.error("No image URL found in card data.")
            raise Exception("No image URL found in card data")
        
        logger.info(f"Card image URL fetched: {card_image_url}")
        
        # Download the image
        image_response = requests.get(card_image_url)
        logger.debug(f"Image download status: {image_response.status_code}")
        
        if image_response.status_code != 200:
            logger.error(f"Failed to download image: {image_response.status_code}")
            raise Exception(f"Failed to download image: {image_response.status_code}")
        
        # Open and resize the image
        img = Image.open(io.BytesIO(image_response.content))
        logger.debug(f"Image dimensions: {img.size}")
        img = img.resize((300, 400), Image.Resampling.LANCZOS)  # Resize for display
        photo = ImageTk.PhotoImage(img)
        
        # Display the image
        label.config(image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        logger.info("Card image displayed successfully.")
        
        #messagebox.showinfo("Card Loaded", f"Card: {card_image_url}")
        
    except Exception as e:
        logger.error(f"Error during card loading: {str(e)}")
        messagebox.showerror("Error", f"Failed to load card: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Momir Card Viewer")
root.geometry("400x500")

# Create a button to load a random card
button = tk.Button(root, text="Load Random Card", command=load_random_card)
button.pack(pady=20)

# Create a label to display the card image
label = tk.Label(root)
label.pack(pady=20)

# Start the GUI event loop
root.mainloop()