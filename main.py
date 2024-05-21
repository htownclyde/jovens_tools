import tkinter.messagebox
import arcane_proxy
import time
import customtkinter # TODO: Dearpygui running in a thread

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

        self.header = customtkinter.CTkLabel(self, text=self.header_name)
        self.header.pack(padx=20, pady=20, anchor=customtkinter.NW, fill=customtkinter.Y)
        ## Tool GUI: arcane_proxy

        self.upload_button = customtkinter.CTkButton(master=self, command=self.upload_button_clicked, text="Load Decklist", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.upload_button.pack(padx=20, pady=20, anchor=customtkinter.W, fill=customtkinter.Y)

        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.pack(padx=20, pady=20, fill=customtkinter.BOTH)
        self.textbox.insert("0.0", "")
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text=">", width=200)
        self.entry.pack(padx=20, pady=20, anchor=customtkinter.SW, fill=customtkinter.Y)
        
        self.print_button = customtkinter.CTkButton(master=self, command=self.print_button_clicked, text="Proxy", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.print_button.pack(padx=20, pady=20, anchor=customtkinter.W, fill=customtkinter.Y)
        
        # Settings Panel
        self.print_dropdown_var = customtkinter.StringVar(value="PDF")  # set initial value
        self.print_dropdown = customtkinter.CTkComboBox(master=self,
                                            values=["PDF", "Receipt"],
                                            command=self.combobox_callback,
                                            variable=self.print_dropdown_var)
        self.print_dropdown.pack(padx=20, pady=10, anchor=customtkinter.W, fill=customtkinter.Y)

    def combobox_callback(self, choice):
        print("combobox dropdown clicked: ", choice)

    def print_button_clicked(self):
        page_type = self.print_dropdown.get()
        current_card = self.entry.get()
        current_decklist = self.textbox.get("0.0", customtkinter.END).split("\n")
        if(len(current_card) > 0):
            self.entry.delete(0, 'end')
            card = arcane_proxy.find_card(current_card)
        elif(len(current_decklist) > 0):
            pdf_images = []
            for line in current_decklist:
                card = arcane_proxy.find_card(line)
                if(page_type == "PDF"):
                    if card is not None:
                        for _ in range(card["quantity"]):
                            pdf_images.append(arcane_proxy.print_card(card, card['quantity'], page_type))
                    time.sleep(0.1) # Temporary delay so I don't get ratelimited - will likely remove
            if(page_type == "PDF"):
                arcane_proxy.create_pdf(pdf_images, 4, 4, "deck.pdf")
        if(card is not None):
            arcane_proxy.print_card(card, card['quantity'], page_type)  # TODO: Create classes and config files for printer/page presets
        
    def upload_button_clicked(self):
        decklist_file = customtkinter.filedialog.askopenfilename(title="Select a Decklist", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        with open(decklist_file, "r") as decklist:
            decklist = decklist.read()
            for line in decklist.split('\n'):
                print(line)
                self.textbox.insert(customtkinter.END, line + '\n')

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

if __name__ == "__main__":
    app = App()
    app.mainloop()