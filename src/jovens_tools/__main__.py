import tkinter.messagebox
from arcane_proxy import arcane_proxy
from tireless_tracker import tireless_tracker
import time
import customtkinter # TODO: Dearpygui running in a thread
import argparse
import logging
import os
from pathlib import Path
import subprocess
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

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

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TirelessTrackerFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="Tireless Tracker", **kwargs):
        super().__init__(*args, **kwargs)
        
        self.header_name = header_name

        self.header = customtkinter.CTkLabel(self, text=self.header_name)
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.label = customtkinter.CTkLabel(self, text="Pardon our dust - this and other tools are under construction")
        self.label.grid(row=1, column=0)

class ArcaneProxyFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="Arcane Proxy", **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name

        # Configure the grid weights so the textbox expands
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header = customtkinter.CTkLabel(self, text=self.header_name)
        self.header.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # Upload Button
        self.upload_button = customtkinter.CTkButton(master=self, command=self.upload_button_clicked, text="Load Decklist", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.upload_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Textbox (set to expand via rowconfigure weight)
        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew", columnspan=2)
        self.textbox.insert("0.0", "")

        # Entry
        self.entry = customtkinter.CTkEntry(self, placeholder_text=">", width=200)
        self.entry.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        # Proxy Button
        self.print_button = customtkinter.CTkButton(master=self, command=self.print_button_clicked, text="Proxy", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.print_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        # Momir Button
        self.momir_button = customtkinter.CTkButton(master=self, command=self.momir_button_cb, text="Momir")
        self.momir_button.grid(row=4, column=1, padx=20, pady=10, sticky="w")

        # Settings Panel (Dropdown)
        self.print_dropdown_var = customtkinter.StringVar(value="Receipt")
        self.print_dropdown = customtkinter.CTkComboBox(master=self,
                                            values=["PDF", "Receipt"],
                                            command=self.combobox_callback,
                                            variable=self.print_dropdown_var)
        self.print_dropdown.grid(row=5, column=0, padx=20, pady=10, sticky="w")

    def combobox_callback(self, choice):
        print("combobox dropdown clicked: ", choice)

    def print_button_clicked(self):
        page_type = self.print_dropdown.get()
        current_card = self.entry.get()
        current_decklist = self.textbox.get("0.0", customtkinter.END).split("\n")
<<<<<<< HEAD
        if(len(current_card) > 0):
            self.entry.delete(0, 'end')
            card = arcane_proxy.find_card(current_card)
=======
        
        if(len(current_card) > 0):
            self.entry.delete(0, 'end')
            card = arcane_proxy.find_card(current_card)
        
>>>>>>> 46e8ba08e7747cceb9f81818403ef44d1fc779a7
        elif(len(current_decklist) > 0):
            pdf_images = []
            for line in current_decklist:
                card = arcane_proxy.find_card(line)
<<<<<<< HEAD
                if(page_type == "PDF"):
                    if card is not None:
                        for _ in range(card["quantity"]):
                            pdf_images.append(arcane_proxy.print_card(card, card['quantity'], page_type))
                    time.sleep(0.1) # Temporary delay so I don't get ratelimited - will likely remove
            if(page_type == "PDF"):
                arcane_proxy.create_pdf(pdf_images, 4, 4, "deck.pdf")
=======
            
                if card is not None:
                    if(page_type == "PDF"):
                        for _ in range(card["quantity"]):
                            pdf_images.append(arcane_proxy.print_card(card, 1, page_type))
                    
                    else:
                        arcane_proxy.print_card(card, card['quantity'], page_type)
                
                time.sleep(0.1) # Temporary delay so I don't get ratelimited - will likely remove
            
            if(page_type == "PDF"):
                arcane_proxy.create_pdf(pdf_images, 4, 4, "deck.pdf")
        
>>>>>>> 46e8ba08e7747cceb9f81818403ef44d1fc779a7
        if(card is not None):
            arcane_proxy.print_card(card, card['quantity'], page_type)  # TODO: Create classes and config files for printer/page presets
        
    def momir_button_cb(self):
        cmc = self.entry.get()
        card = tireless_tracker.momir(cmc)
        print(f"momir vig found a {card}")

    def upload_button_clicked(self):
        decklist_file = customtkinter.filedialog.askopenfilename(title="Select a Decklist", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
<<<<<<< HEAD
        with open(decklist_file, "r") as decklist:
            decklist = decklist.read()
            for line in decklist.split('\n'):
                print(line)
                self.textbox.insert(customtkinter.END, line + '\n')
=======
        try:
            with open(decklist_file, "r") as decklist:
                decklist = decklist.read()
                for line in decklist.split('\n'):
                    print(line)
                    self.textbox.insert(customtkinter.END, line + '\n')
        except FileNotFoundError:
            print("Failed to open: %s", str(decklist_file))
        except TypeError:
            print("Deck selection dialogue closed")
>>>>>>> 46e8ba08e7747cceb9f81818403ef44d1fc779a7

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Joven's Tools")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Joven's Tools", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.arcane_proxy_button = customtkinter.CTkButton(self.sidebar_frame, command=self.arcane_proxy_button_callback, text="Arcane Proxy")
        self.arcane_proxy_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.tireless_tracker_button = customtkinter.CTkButton(self.sidebar_frame, command=self.tireless_tracker_button_callback, text="Tireless Tracker")
        self.tireless_tracker_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        # app frame
        container = customtkinter.CTkFrame(self)
        container.grid(row=0, column=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tireless_tracker_frame = TirelessTrackerFrame(self)
        self.tireless_tracker_frame.grid(row=0, column=1, sticky="NSEW")

        self.arcane_proxy_frame = ArcaneProxyFrame(self)
        self.arcane_proxy_frame.grid(row=0, column=1, sticky="NSEW")

        self.frames = {}

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def arcane_proxy_button_callback(self):
        print("arcane_proxy click")
        self.arcane_proxy_frame.tkraise()

    def tireless_tracker_button_callback(self):
        print("tireless_tracker click")
        self.tireless_tracker_frame.tkraise()

parser = argparse.ArgumentParser(description="arcane_proxy arguments")
parser.add_argument("--debug", "-d", action='store_true', help="enable debug mode")
parser.add_argument("--gui", "-g", action='store_true', help="launch the gui (wip)")
args = parser.parse_args()
if args.debug:
    log.debug("main: debug mode enabled - will not print cards")
    log.setLevel(logging.DEBUG)

def cli():
    help_text = "\n[jovens_tools]\n\n" \
    "some commands you can try:\n" \
    "   scry <query>: returns a scryfall search result\n" \
    "   momir <cmc>: returns a random creature of this cmc\n" \
    "   printer <index>: someone set us up the printer\n" \
    "   query <query>: edit default search query - ex. 't:creature in:paper'\n" \
    "   help: print this menu\n" \
    "   exit/quit: exit/quit\n"
    print(help_text)
    search_query = f"t:creature in:paper"
    printer_path = "/dev/usb/lp0"
    session = PromptSession(history=FileHistory('.history'))
    while (1):
        try:
            cmd = session.prompt("> ")
        except KeyboardInterrupt:
            print("exiting...")
            break
        match cmd.split(" ")[0]:
            case "help":
                print(help_text)
            case "momir":
                cmc = cmd.split(" ")[1]
                cmc = cmc.strip() 
                try:
                    # Try converting to an integer
                    value = int(cmc)
                    # Check if the integer is positive
                    if value > 0:
                        card = tireless_tracker.momir(cmc, search_query)
                        arcane_proxy.print_card(card.card_json)
                    else:
                        print(f"cli: invalid cmc {cmc}")
                except ValueError:
                    print(f"cli: invalid cmc {cmc}")
                    return None
            case "scry":
                card_query = cmd.split(" ", 1)[1]
                card = tireless_tracker.parse_card_line(card_query)
                card.scry_fetch()
                arcane_proxy.print_card(card.card_json)
            case "printer":
                #print("available printers:")
                #printers = arcane_proxy.list_printers()
                #i = 0
                #for printer in printers:
                #    i += 1
                #    print(f"{i}: {printer}")
                #print(f"default: {arcane_proxy.get_default_printer()}\n")
                #result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
                #lines = result.stdout.strip().split('\n')
                #printers = [line for line in lines if 'printer' in line.lower() or 'epson' in line.lower()]
                #print(printers)
                print(f"current printer path is {printer_path}")
                try:
                    new_printer_path = input(f"enter printer /dev/ path (or press enter to skip): ")
                except KeyboardInterrupt:
                    ...
                if (new_printer_path is not ""):
                    if(arcane_proxy.test_printer(new_printer_path)):
                        printer_path = new_printer_path
                        print(f"new path is {printer_path}")
                print("")
            case "query":
                print(f"current query is {search_query}")
                try:
                    new_query = cmd.split(" ", 1)[1]
                except Exception as e:
                    new_query = input(f"paste the new query (or press enter to skip): ")
                if (":" in new_query):
                    if(tireless_tracker.scry_validate(new_query)):
                        search_query = new_query
                        print(f"new query is {search_query}")
                else:
                    print("invalid query - try again")
            case "exit":
                break
            case "quit":
                break
            case _:
                print("invalid command, type 'help' to list valid commands")

def main():
    # Create a console handler and set the level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and attach it to the console handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    log.addHandler(console_handler)

    if args.gui:
        app = App()
        try:
            app.mainloop()
        except KeyboardInterrupt:
            print("Exiting!")
    else:
        try:
            cli()
        except KeyboardInterrupt:
            print("Exiting...")

if __name__ == "__main__":
    main()