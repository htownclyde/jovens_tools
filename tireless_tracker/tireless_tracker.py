
import os
import time
import argparse
import requests
import logging
from pathlib import Path

log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = f"{Path(__file__).name}_{round(time.time())}.log"

try:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=os.path.join(log_directory, log_file),
        filemode='a'
    )
except Exception as e:
    print("failed to set up logging - trying again without logfile")
    # Configure logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Create a logger
log = logging.getLogger()

# Create a console handler and set the level
if not log.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and attach it to the console handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    log.addHandler(console_handler)

class card:
    name: str = None
    quantity: int = 1
    set_code: str = None
    def __init__(self, name):
        self.name = name

    def scry_fetch(self, query=None, params=None, endpoint="named"):
        """Attempt to fetch the card's info from Scryfall to populate the object"""
        # TODO: Figure out the best way to have multiple avenues of populating the card info (JSON, SQL, scryfall, etc)
        # TODO: This needs to respect set codes (and other things) if already specified
        if not query:
            query = self.name
        default_scry_params = {
            'fuzzy': query if query else None,
            'unique': 'prints',
        }
        if not params:
            params = default_scry_params
        # Scryfall API endpoint for card search
        # TODO: Option to ignore digital-only cards - also make this some kind of modular source class
        api_url = f'https://api.scryfall.com/cards/{endpoint}'

        log.debug(f"scry_fetch: making request w/ params {params}")

        # Make the GET request to the Scryfall API
        response = requests.get(api_url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            card_data = response.json()

            # Check if any cards were found
            if card_data:
                # Display information about the first card found
                if ("card_faces" in card_data.keys()):
                    card_data = card_data["card_faces"][0]

                if args.debug:
                    for key in card_data:
                        print(f"{key} - {card_data[key]}")
                card_data['quantity'] = self.quantity if self.quantity else card_data['quantity']
                log.info(f"find_card: card Name: {card_data['name']}")

                try:
                    log.info(f"find_card: set: {card_data['set_name']} ({card_data['set']})")
                except:
                    log.warning("find_card: set not found for card: %s", card_data["name"])
            else:
                log.error("find_card: no matching cards found.")
        else:
            log.error(f"scry_fetch: got ({response.status_code}) with params {params}")

def parse_card_line(query):
    """Parses queries like '2 Arcbound Ravager (MDN)' from decklists"""
    # TODO: Use regex config files referencing formats from major decklist sites
    # TODO: This should be part of a larger decklist import fn
    set_code = ""
    
    # Extract set codes like '(MDN)' or '[FNM]'
    # TODO: Support for Tappedout codes like '(CMDR)' or '[S]'
    if '[' in query or '(' in query:
        query = query.replace('[', '(')
        query = query.replace(']', ')')
        query = query.split('(', 1)
        query[1] = query[1].split(')', 1)[0].strip()
        set_code = query.pop(1).lower()
        query = query[0]

    # Extract card quantity like '2' or '2x'
    if query.split(" ", 1)[0].strip("x").isdigit():
        query = query.split(" ", 1)
        query[0] = query[0].strip("x")

    query_card = card(query)
    query_card.set_code = set_code
    return query_card

def momir(cmc):
    momir_card = card(None)
    search_query = f"t:creature mv:{cmc}"
    
    params = {
        'q': search_query
    }
    momir_card.scry_fetch(query=None, params=params, endpoint="random")

parser = argparse.ArgumentParser(description="arcane_proxy arguments")
parser.add_argument("--debug", "-d", action='store_true', help="enable debug mode")
parser.add_argument("--momir", "-m", action='store_true', help="enable momir mode")
args = parser.parse_args()
if args.debug:
    log.debug("main: debug mode enabled - will not print cards")
    log.setLevel(logging.DEBUG)

# TODO: Config function to easily manage Scryfall (or DB) search parameter preferences
if __name__ == "__main__":
    intro_string = "Demo: Enter a card name to find it!"
    if args.momir:
        intro_string = "Momir: Enter a CMC for your creature!"
    print(intro_string)
    while (1):
        try:
            query = input("> ")
        except KeyboardInterrupt:
            print("Exiting...")
            break
        if args.momir:
            momir(query)
        else:
            query_card = parse_card_line(query)
            query_card.scry_fetch()