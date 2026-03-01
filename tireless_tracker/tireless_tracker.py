
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

def scry_validate(query):
    """
    Checks if a string is a valid Scryfall search query.
    """
    base_url = "https://api.scryfall.com/cards/search"
    params = {"q": query}
    
    try:
        response = requests.get(base_url, params=params)
        # 200 means the query is valid and parsed
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        # TODO: Handle connection errors
        return False

class card:
    card_json = None
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
            card_json = response.json()

            # Check if any cards were found
            if card_json:
                self.card_json = card_json
                # Display information about the first card found
                if ("card_faces" in self.card_json.keys()):
                    self.card_json = self.card_json["card_faces"][0]

                if args.debug:
                    for key in self.card_json:
                        print(f"{key} - {self.card_json[key]}")
                self.card_json['quantity'] = self.quantity if self.quantity else self.card_json['quantity']
                log.info(f"find_card: card Name: {self.card_json['name']}")

                try:
                    log.info(f"find_card: set: {self.card_json['set_name']} ({self.card_json['set']})")
                except:
                    log.warning("find_card: set not found for card: %s", self.card_json["name"])
            else:
                log.error("find_card: no matching cards found.")
        else:
            log.error(f"scry_fetch: got ({response.status_code}) with params {params}")

    def parse_json(self, card_json=None):
        # TODO: Program needs way cleaner input handling (and validation of data)
        if not card_json:
            card_json = self.card_json
            if not card_json:
                log.error(f"card: json for {self.name} invalid - {self.card_json}")
                return False
        # TODO: Populate card object w/ data from JSON here
        log.error("UNIMPLEMENTED")
        # toughness, artist, etc

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

def momir(cmc, search_query=f"t:creature in:paper"):
    momir_card = card(None)
    # TODO: Easily configurable query objects!
    search_query += f" mv:{cmc}"
    
    params = {
        'q': search_query
    }
    momir_card.scry_fetch(query=None, params=params, endpoint="random")
    return momir_card

parser = argparse.ArgumentParser(description="arcane_proxy arguments")
parser.add_argument("--debug", "-d", action='store_true', help="enable debug mode")
parser.add_argument("--momir", "-m", action='store_true', help="enable momir mode")
args = parser.parse_args()
if args.debug:
    log.debug("main: debug mode enabled - will not print cards")
    log.setLevel(logging.DEBUG)

# TODO: Config function to easily manage Scryfall (or DB) search parameter preferences
if __name__ == "__main__":
    # Create a console handler and set the level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and attach it to the console handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    log.addHandler(console_handler)

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