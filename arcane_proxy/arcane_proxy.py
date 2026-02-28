import os
import io
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageWin
from escpos import *
from escpos.printer import *
import StarTSPImage
import subprocess
from requests import get
from json import loads
import math
from shutil import copyfileobj
import logging
import os
import requests
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# TODO: REMOVE ALCHEMY!!!
filedir=os.path.dirname(os.path.abspath(__file__))
img_path = ""

# Configure logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='arcane_proxy.log',
    filemode='a'
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

pdf_images = []

def print_card(card, quantity, page_type="Receipt"):    # TODO: Create proper method for handling page type setup/configuration on unix/nt
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
    font_name = "trebuc.ttf"
    while(1):
        try:
            font = ImageFont.truetype(font_name, 80)
            font_s = ImageFont.truetype(font_name, 40)
            break
        except OSError:
            logging.error("Font not installed. Type the name of a .ttf you have installed: ")
            font_name = input("> ")
    # TODO: Construct full card proxy with set code, etc, all aligned and resized
    #card_drawing.rectangle((0, 180, height, width), fill=(255, 255, 255))
    try:
        card_drawing.text((0, 0), card['mana_cost'], fill=(0, 0, 0), font=ImageFont.truetype(font_name, round(78-len(card['mana_cost']))), stroke_width=2)
    except:
        logging.error("Could not populate CMC")
    card_drawing.text((10, 85), card['name'], fill=(0, 0, 0), font=ImageFont.truetype(font_name, round(78-len(card['name']))), stroke_width=2)
    #card_drawing.rectangle((0, 500, width, height), fill=(255, 255, 255))
    card_drawing.text((10, 500), card['type_line'], fill=(0, 0, 0), font=ImageFont.truetype(font_name, round(40-len(card['type_line'])/8)), stroke_width=2)
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
    for _ in range(quantity):       # TODO: Find a better method for printing on Windows...
        if(page_type == "Receipt"):
            if(os.name == "nt"):        # Call a MSPaint print subprocess if this program is running on Windows

                subprocess.call("mspaint /pt card.bmp")
            else:                       # Create a raster and write to /dev/lp0 if running on Linux
                raster = StarTSPImage.imageFileToRaster("card.bmp", True)
                try:
                    with open('/dev/usb/lp0', 'wb') as printer:
                        printer.write(raster)
                except PermissionError:
                    logging.error("Permission to open printer denied.\nPlease run this application as administrator or grant the user permissions")
        elif(page_type == "PDF"):
            pdf_images.append(original_card)
        else:
            logging.error("Unknown page type enumeration.")
    return original_card

def create_collage(rows, columns, images, width=round(6120/2.5), height=round(7920/2.5)):
    image_sets = []
    page_images = []
    images_per_page = rows*columns
    pages = math.ceil(len(images)/images_per_page)
    for page in range(pages):
        image_sets.append([])
        for i, p in enumerate(images):
            page = i % images_per_page
            print(page)
            im = p.rotate(90)
            img_box = im.getbbox()
            im = im.crop(img_box)
            img_width, img_height = im.size
            im.thumbnail(im.size)
            image_sets[len(image_sets)-1].append(im)
        new_im = Image.new('RGB', (width, height))
        y_offset = 40
        i = 0   # Image
        x = 0
        y = y_offset
        for index, page_set in enumerate(image_sets):
            for col in range(columns):
                for row in range(rows):
                    try:
                        print(i, x, y)
                        new_im.paste(page_set[i], (x, y))
                        i += 1
                        y += img_height + y_offset
                    except:
                        logging.warning("fix this indexerror later")
                x += img_width
                y = y_offset

            new_im.save("page.bmp")
            page_images.append(new_im)
            logging.info("Created page image: %s", index)
    return page_images

def create_pdf(pdf_images, rows, columns, output_filename="deck.pdf"):
    pages = create_collage(rows, columns, pdf_images)
    pdf_canvas = canvas.Canvas(output_filename, pagesize=letter)
    width, height = letter
    print("%f %f", width, height)
    for page in pages:
        page.save("pdf_image.bmp")
        img_canvas = canvas.Canvas("img_pdf.pdf", pagesize=letter)
        img_canvas.drawImage("pdf_image.bmp", 0, 0, width=600, height=820)
        img_canvas.showPage()
    img_canvas.save()
    logging.info("Saving PDF...")
    try:
        pdf_canvas.save()
        logging.info("Saved PDF.")
    except:
        logging.error("Failed to save PDF")

def find_card(query):
    card_data = None
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
    api_url = 'https://api.scryfall.com/cards/named'

    # Parameters for the card search
    params = {
        'fuzzy': query,
        'unique': 'prints',
    }

    # Make the GET request to the Scryfall API
    response = requests.get(api_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        card_data = response.json()
        # Check if any cards were found
        if card_data:
            # Display information about the first card found
            
            if("card_faces" in card_data.keys()):
                card_data = card_data["card_faces"][0]
            for stuff in card_data:
                print(stuff)
            card_data['quantity'] = card_quantity
            logging.info(f"Card Name: {card_data['name']}")
            try:
                logging.info(f"Set: {card_data['set_name']} ({card_data['set']})")
            except:
                logging.warn("Set not found for card: %s", card_data["name"])
            try:
                logging.info(f"Mana Cost: {card_data['mana_cost']}")
            except:
                card_data['mana_cost'] = "{0}"
            logging.info(f"Type: {card_data['type_line']}")
            try:
                logging.info(f"Oracle Text: {card_data['oracle_text']}")
            except:
                card_data['oracle_text'] = "ORACLE TEXT ERROR"
            logging.debug("Found card: %s" %card_data.keys())
        else:
            logging.error("No matching cards found.")
    else:
        logging.error(f"Error: {response.status_code}")
    
    return card_data


if __name__ == "__main__":
    while 1:
        card = None
        try:
            card = find_card(input("> "))
        except KeyboardInterrupt:
            logging.info("Received keyboard interrupt - exiting program.")
            break
        except KeyError as e:
            logging.info("DEBUG - failed: %s", e)
        if card is not None:
            print_card(card, card['quantity'])