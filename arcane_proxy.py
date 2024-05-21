import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageWin
from escpos import *
from escpos.printer import *
from win32 import win32print
import StarTSPImage
import subprocess
from requests import get
from json import loads
from shutil import copyfileobj
import logging
import os
import requests

# TODO: REMOVE ALCHEMY!!!
filedir=os.path.dirname(os.path.abspath(__file__))
img_path = ""

# Configure the logging module
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='example.log',  # Specify the log file name
    filemode='a'  # Use 'a' to append to the log file, 'w' to overwrite
)

# Create a logger
logger = logging.getLogger()
# Create a console handler and set the level to DEBUG
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and attach it to the console handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

# TODO: Store images to folders, save file nicknames, lists, etc.
link_list, image_list = [], []
image_pointer = 0

def print_card(card, quantity):
    card_image_bytes = requests.get(card['image_uris']['art_crop']).content
    original_card = Image.new('RGB', (750, 1040), (255, 255, 255))
    card_image = Image.open(BytesIO(card_image_bytes)).resize((750, 330))
    original_card.paste(card_image, (0, 160))
    km = (
     -2, -1,  0,
     -1,  1,  1,
      0,  1,  2
      )
    original_card = original_card.filter(ImageFilter.Kernel(
    size=(3, 3),
    kernel=km,
    scale=sum(km),  # default
    offset=0  # default
    ))
    width = original_card.width
    height = original_card.height
    card_drawing = ImageDraw.Draw(original_card)
    card_drawing.point((width, height), fill=(0, 0, 0))
    font = ImageFont.truetype("arial.ttf", 80)  # You can specify the font and size you prefer
    font_s = ImageFont.truetype("arial.ttf", 40)  # You can specify the font and size you prefer
    # TODO: Construct full card proxy with set code, etc, all aligned and resized
    #card_drawing.rectangle((0, 180, height, width), fill=(255, 255, 255))
    try:
        card_drawing.text((0, 0), card['mana_cost'], fill=(0, 0, 0), font=ImageFont.truetype("arial.ttf", round(78-len(card['mana_cost']))), stroke_width=2)
    except:
        logging.error("Could not populate CMC")
    card_drawing.text((10, 85), card['name'], fill=(0, 0, 0), font=ImageFont.truetype("arial.ttf", round(78-len(card['name']))), stroke_width=2)
    #card_drawing.rectangle((0, 500, width, height), fill=(255, 255, 255))
    card_drawing.text((10, 500), card['type_line'], fill=(0, 0, 0), font=ImageFont.truetype("arial.ttf", round(40-len(card['type_line'])/8)), stroke_width=2)
    card_drawing.line((0, 550, width, 550), fill=(0, 0, 0), width=2)
    rulestext = ""
    linelength = 0
    try:
        for word in card['oracle_text'].split(" "):
            linelength += len(word + " ")
            if(linelength>37):
                rulestext += "\n"
                linelength = 0
            rulestext += word + " "
        card_drawing.text((10, 550), rulestext, fill=(0, 0, 0), font=font_s)
        card_drawing.text((11, 550), rulestext, fill=(0, 0, 0), font=font_s)
    except:
        logging.error("Could not process oracle text for: %s" %card['name'])
        card_drawing.text((10, 550), "ERROR: NO ORACLE TEXT LOL", fill=(0, 0, 0), font=font_s)
    try:
        flavortext = ""
        linelength = 0
        for word in card['flavor_text'].split(" "):
            linelength += len(word + " ")
            if(linelength>35):
                flavortext += "\n"
                linelength = 0
            flavortext += word + " "
        if len(rulestext)<40*6: card_drawing.text((10, height-200), flavortext, fill=(0, 0, 0), font=font_s)
    except:
        ...
    try:
        if "Creature" in card['type_line']:
            pt = "({}/{})".format(card['power'], card['toughness'])
            card_drawing.rectangle((20+width-len(pt)*55, height-100, width, height), fill=(255, 255, 255))
            card_drawing.text((width-len(pt)*35, height-100), pt, fill=(0, 0, 0), font=font, stroke_width=2)
    except:
        logging.error("Could not populate power or toughness")
    if "Planeswalker" in card['type_line']:
        card_drawing.rectangle((width-120, height-100, width, height), fill=(255, 255, 255))
        card_drawing.text((width-100, height-100), "[{}]".format(card['loyalty']), fill=(0, 0, 0), font=font, stroke_width=2)
    original_card = original_card.rotate(270, expand="true")
    #original_card.show()
    original_card.save('card.bmp')
    absolute_path = os.getcwd() + '\{}.png'.format(card['name'])
    with open('card[\'name\'].txt', 'w') as file:
        file.write(card['name'])
    file.close()
    for _ in range(quantity):
        if(os.name == "nt"):        # Call the win32print API if this program is running on Windows
            #printer_name = win32print.GetDefaultPrinter()
            #printer_handle = win32print.OpenPrinter(printer_name)
            #win32print.StartDocPrinter(printer_handle, 1, ("sideboard_guide", None, "raw"))
            #win32print.WritePrinter(printer_handle, open("card.bmp", 'rb').read())
            subprocess.call("mspaint /pt card.bmp")
        else:                       # Create a raster and write to /dev/lp0 if running on Linux
            raster = StarTSPImage.imageFileToRaster("card.bmp", True)
            with open('/dev/usb/lp0', 'wb') as printer:
                printer.write(raster)

def find_card(query):
    card = None
    set_code = None
    card_quantity = 1
    if '[' in query or '(' in query:
        query = query.replace('[', '(')
        query = query.replace(']', ')')
        query = query.split('(', 1)
        query[1] = query[1].split(')', 1)[0].strip()
        set_code = query.pop(1).lower()
        query = query[0]
    if query.split(" ", 1)[0].strip("x").isdigit():
        query = query.split(" ", 1)
        query[0] = query[0].strip("x")
        card_quantity = min(int(query.pop(0)), 20)
        if card_quantity == 20:
            logging.warn("Card quantity limited to 20")

    # Scryfall API endpoint for card search
    api_url = 'https://api.scryfall.com/cards/search'

    # Parameters for the card search
    params = {
        'q': query,
        'unique': 'prints'
    }

    # Make the GET request to the Scryfall API
    response = requests.get(api_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        for stuff in data:
            print(stuff)
        # Check if any cards were found
        if data['total_cards'] > 0:
            # Display information about the first card found
            print(set_code)
            for printing in data['data']:   # TODO: Fix exact match issue
                print(printing['set'])
                if printing['set'] == set_code:
                    card = printing
            if card == None:
                card = data['data'][0]
            card['quantity'] = card_quantity
            logging.info(f"Card Name: {card['name']}")
            logging.info(f"Set: {card['set_name']} ({card['set']})")
            logging.info(f"Mana Cost: {card['mana_cost']}")
            logging.info(f"Type: {card['type_line']}")
            logging.info(f"Oracle Text: {card['oracle_text']}")
            logging.debug("Found card: %s" %card.keys())
        else:
            logging.error("No matching cards found.")
    else:
        logging.error(f"Error: {response.status_code}")
    
    return card


if __name__ == "__main__":
    while 1:
        card = None
        try:
            card = find_card(input("> "))
        except KeyboardInterrupt:
            logging.info("Received keyboard interrupt - exiting program.")
            break
        except KeyError:
            logging.info("DEBUG - failed to fetch, work on this handling!")
        if card is not None:
            print_card(card, card['quantity'])