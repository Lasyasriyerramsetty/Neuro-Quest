import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk # Import ttk for themed widgets and styling
import random
import time
import winsound
from PIL import Image, ImageTk
import os

# --- Theme Presets with PNG Images and Backgrounds ---
LEVEL_THEMES = {
    1: {  # Easy / Level 1
        "name": "🌲 Enchanted Forest",
        "bg_color": "#1a2332",
        "bg_image": "forest_bg.png",
        "card_back_color": "#34495e",
        "accent_color": "#09ec68",
        "text_color": "#ecf0c1",
        "font_large": ("Comic Neue", 28, "italic"),
        "font_medium": ("Arial", 16),
        "font_small": ("Arial", 12),
        "card_images": ["owl.png", "mushroom.png", "tree.png", "butterfly.png", "deer.png", "lion.png"],
        "time_limit": 40,
        "grid_size": (4, 3)
    },
    2: {  # Medium / Level 2
        "name": "🌊 Under the Sea",
        "bg_color": "#a9cfd1",
        "bg_image": "sea_bg.png",
        "card_back_color": "#116466",
        "accent_color": "#191970",
        "text_color": "#2B2D42",
        "font_large": ("Comic Neue", 28, "italic"),
        "font_medium": ("Arial", 16),
        "font_small": ("Arial", 12),
        "card_images": ["fish.png", "jelly_fish.png", "octopus.png", "star_fish.png", "crab.png", "dolphin.png", "clown_fish.png", "seahorse.png"],
        "time_limit": 60,
        "grid_size": (4, 4)
    },
    3: {  # Challenge / Level 3
        "name": "⚙️ Steampunk Clockwork",
        "bg_color": "#2c1810",
        "bg_image": "steampunk_bg.png",
        "card_back_color": "#4a3728",
        "accent_color": "#E49B49",
        "text_color": "#f4e4bc",
        "font_large": ("Comic Neue", 28, "italic"),
        "font_medium": ("Arial", 16),
        "font_small": ("Arial", 12),
        "card_images": ["bolt.png", "gear.png", "clock.png", "tools.png", "wrench.png", "compass.png", "satellite.png", "bulb.png", "battery.png", "hourglass.png"],
        "time_limit": 80,
        "grid_size": (4, 5)
    }
}
# ───────────────────────────────────────────────────────────────────────────────

class NeuroQuestGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Neuro Quest - Memory Challenge")
        self.root.geometry("800x800")
        self.root.resizable(True, True)

        if not os.path.exists("images"):
            os.makedirs("images")
            messagebox.showinfo("Info", "Created 'images' folder. Please add your card images (PNG) and background images (PNG) there.")

        self.image_references = []
        self.pil_image_cache = {}

        self.level = None
        self.buttons = []
        self.flipped = []
        self.matched = []
        self.locked = False
        self.total_score = 0
        self.time_remaining = 0
        self.time_limit = 0
        self.card_size = (100, 100)

        self.player_name = "Player"

        self.leaderboard_data = {
            1: [],
            2: [],
            3: []
        }
        self.load_leaderboard()

        self.menu_bg_image_filename = "cardback.png"

        # Define the path to your custom mouse click sound file here (should be a WAV)
        self.mouse_click_sound_file = "mouse_click.wav" # <--- Ensure this matches your WAV file name

        self.setup_main_menu()

    def play_button_click_sound(self):
        """Plays a custom mouse click sound from a WAV file, or a default beep if the file isn't found."""
        try:
            # Check if the WAV file exists
            if os.path.exists(self.mouse_click_sound_file):
                # winsound.SND_ASYNC plays the sound asynchronously, so it doesn't freeze the GUI
                winsound.PlaySound(self.mouse_click_sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                # Fallback to a simple beep if the WAV file is not found
                winsound.Beep(440, 50)
                # print(f"Warning: '{self.mouse_click_sound_file}' not found. Playing default beep.") # For debugging
        except Exception as e:
            # print(f"Could not play button sound: {e}") # Debugging
            # Fallback to a simple beep if any error occurs (e.g., winsound not available)
            try:
                winsound.Beep(440, 50)
            except:
                pass # Fail silently if winsound isn't available at all

    def play_button_click_sound_on_tab_change(self, event=None):
        """Plays the button click sound when a notebook tab is changed."""
        self.play_button_click_sound()

    def load_and_resize_image(self, filename, target_width, target_height, for_background=False):
        """
        Loads an image using Pillow, resizes it with high quality.
        - If 'for_background' is True, it scales and crops to fill the target dimensions.
        - If 'for_background' is False (for card images), it scales directly to target_width x target_height,
          potentially distorting aspect ratio to make the image occupy the complete card.
        Returns a Tkinter PhotoImage object.
        """
        try:
            image_path = os.path.join("images", filename)

            # Use cache for background images if already loaded
            if for_background and filename in self.pil_image_cache:
                original_pil_img = self.pil_image_cache[filename]
            else:
                original_pil_img = Image.open(image_path)
                if for_background:
                    self.pil_image_cache[filename] = original_pil_img.copy() # Cache a copy

            # Convert to RGBA if not already for consistent alpha handling
            if original_pil_img.mode != "RGBA":
                original_pil_img = original_pil_img.convert("RGBA")

            original_width, original_height = original_pil_img.size

            if for_background:
                # For backgrounds, resize to fill the target dimensions, cropping if necessary
                aspect_ratio = original_width / original_height
                target_aspect_ratio = target_width / target_height

                if aspect_ratio > target_aspect_ratio:
                    # Original image is wider than target, crop width
                    new_height = target_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    # Original image is taller or same aspect ratio, crop height
                    new_width = target_width
                    new_height = int(new_width / aspect_ratio)

                resized_pil_img = original_pil_img.resize((new_width, new_height), Image.LANCZOS)

                # Crop if necessary to fit exact target dimensions
                left = (new_width - target_width) / 2
                top = (new_height - target_height) / 2
                right = (new_width + target_width) / 2
                bottom = (new_height + target_height) / 2
                resized_pil_img = resized_pil_img.crop((left, top, right, bottom))

                final_img = resized_pil_img

            else: # For card images - directly resize to fill the target, potentially distorting aspect ratio
                final_img = original_pil_img.resize((target_width, target_height), Image.LANCZOS)

            tk_image = ImageTk.PhotoImage(final_img)

            # IMPORTANT: Keep a strong reference to the Tkinter PhotoImage object!
            # Otherwise, Tkinter's garbage collector might delete it, and it won't display.
            self.image_references.append(tk_image)
            return tk_image

        except FileNotFoundError:
            error_msg = f"Image file not found: '{filename}'. Please ensure it exists in the 'images' folder."
            messagebox.showwarning("Image Loading Error", error_msg)
            return None
        except Exception as e:
            error_msg = f"An unexpected error occurred while loading or processing image: '{filename}'. Error: {e}"
            messagebox.showwarning("Image Processing Error", error_msg)
            import traceback
            traceback.print_exc() # Print full traceback for detailed error info
            return None

    def setup_background(self, bg_image_filename, bg_color):
        # Clear existing background label if any
        if hasattr(self, '_background_label') and self._background_label is not None:
            self._background_label.destroy()
            del self._background_label

        # Set root background color as fallback/base
        self.root.configure(bg=bg_color)

        # Get current window size to resize background image appropriately
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        bg_image_tk = self.load_and_resize_image(bg_image_filename, window_width, window_height, for_background=True)

        if bg_image_tk:
            self._background_label = tk.Label(self.root, image=bg_image_tk)
            self._background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self._background_label.lower() # Place it behind other widgets
        else:
            self._background_label = None # No background image set
   

    def clear_widgets(self):
        # Stop any ongoing animations/timers before clearing
        if hasattr(self, '_timer_id') and self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        if hasattr(self, '_shake_id') and self._shake_id:
            self.root.after_cancel(self._shake_id)
            self._shake_id = None
        if hasattr(self, '_win_effect_id') and self._win_effect_id:
            self.root.after_cancel(self._win_effect_id)
            self._win_effect_id = None


        for w in self.root.winfo_children():
            if w is not getattr(self, '_background_label', None):
                w.destroy()
        self.buttons.clear()
        self.image_references.clear() # Clear references to allow images to be garbage collected
        self.pil_image_cache.clear() # Clear PIL image cache too

    def setup_main_menu(self):
        self.clear_widgets()
        current_theme = LEVEL_THEMES[1] # Use level 1 theme for main menu frame's solid background color

        # Set the main window background to cardback.png
        self.setup_background(self.menu_bg_image_filename, current_theme["bg_color"])

        main_menu_frame = tk.Frame(self.root, bg=current_theme["bg_color"], bd=5, relief="raised")
        main_menu_frame.place(relx=0.5, rely=0.5, anchor="center") # Center the frame

        # Main title with gradient effect
        title = tk.Label(main_menu_frame,
                         text="🧠 NEURO QUEST 🧠",
                         font=("Arial Black", 32, "bold"),
                         bg=current_theme["bg_color"],
                         fg="#f39c12") # Orange color for title
        title.pack(pady=(30, 5))

        subtitle = tk.Label(main_menu_frame,
                             text="🌟 Ultimate Memory Challenge 🌟",
                             font=("Arial", 16, "italic"),
                             bg=current_theme["bg_color"],
                             fg=current_theme["text_color"])
        subtitle.pack(pady=(0, 30))

        # Button frame
        button_frame = tk.Frame(main_menu_frame, bg=current_theme["bg_color"])
        button_frame.pack(pady=20)

        # Start Game Button (now leads to name input)
        start_btn = tk.Button(button_frame,
                               text="🎯 START GAME",
                               font=current_theme["font_medium"],
                               bg="#27ae60", # Green
                               fg="white",
                               activebackground="#2ecc71",
                               relief="flat",
                               padx=30,
                               pady=15,
                               cursor="hand2",
                               command=lambda: (self.play_button_click_sound(), self.get_player_name()))
        start_btn.pack(pady=10)

        # Instructions Button
        instructions_btn = tk.Button(button_frame,
                                     text="📋 HOW TO PLAY",
                                     font=current_theme["font_medium"],
                                     bg="#3498db", # Blue
                                     fg="white",
                                     activebackground="#5dade2",
                                     relief="flat",
                                     padx=30,
                                     pady=15,
                                     cursor="hand2",
                                     command=lambda: (self.play_button_click_sound(), self.show_instructions()))
        instructions_btn.pack(pady=10)

        # Leaderboard Button
        leaderboard_btn = tk.Button(button_frame,
                                     text="🏆 LEADERBOARD",
                                     font=current_theme["font_medium"],
                                     bg="#8e44ad", # Purple
                                     fg="white",
                                     activebackground="#9b59b6",
                                     relief="flat",
                                     padx=30,
                                     pady=15,
                                     cursor="hand2",
                                     command=lambda: (self.play_button_click_sound(), self.show_leaderboard()))
        leaderboard_btn.pack(pady=10)


        # Exit Button
        exit_btn = tk.Button(button_frame,
                               text="❌ EXIT",
                               font=current_theme["font_medium"],
                               bg="#e74c3c", # Red
                               fg="white",
                               activebackground="#ec7063",
                               relief="flat",
                               padx=30,
                               pady=15,
                               cursor="hand2",
                               command=lambda: (self.play_button_click_sound(), self.exit_game()))
        exit_btn.pack(pady=(10, 30))

    def get_player_name(self):
        # This will be a Toplevel window for name input
        name_popup = tk.Toplevel(self.root)
        name_popup.title("Enter Your Name")
        name_popup.transient(self.root) # Make it appear on top of the main window
        name_popup.grab_set() # Make it modal
        name_popup.resizable(False, False)

        popup_width = 400
        popup_height = 200
        # Calculate position to center the popup
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        popup_x = main_x + (main_width // 2) - (popup_width // 2)
        popup_y = main_y + (main_height // 2) - (popup_height // 2)
        name_popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

        current_theme = LEVEL_THEMES[1] # Use a theme for colors
        name_popup.config(bg=current_theme["bg_color"])

        tk.Label(name_popup, text="What's your name, Memory Master?",
                 font=("Arial", 16, "bold"), fg=current_theme["accent_color"], bg=current_theme["bg_color"]).pack(pady=20)

        name_entry = tk.Entry(name_popup, font=("Arial", 14), width=25, justify="center")
        name_entry.insert(0, self.player_name) # Pre-fill with current name or default
        name_entry.pack(pady=10)
        name_entry.focus_set() # Automatically focus the entry field

        def start_game_with_name():
            entered_name = name_entry.get().strip()
            if entered_name:
                self.player_name = entered_name
                name_popup.destroy()
                self.play_button_click_sound() # Play sound for "Let's Play" click
                self.setup_level_selection()
            else:
                messagebox.showwarning("Name Required", "Please enter a name to start the game!")

        # Bind Enter key to start game
        name_entry.bind("<Return>", lambda event=None: start_game_with_name())

        ok_button = tk.Button(name_popup, text="Let's Play!", command=start_game_with_name,
                              font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                              activebackground="#2ecc71", relief="flat", padx=20, pady=10, cursor="hand2")
        ok_button.pack(pady=10)

        # If the user closes the popup without entering a name, return to main menu
        name_popup.protocol("WM_DELETE_WINDOW", lambda: (name_popup.destroy(), self.setup_main_menu()))


    def show_instructions(self):
        instructions = """
 HOW TO PLAY NEURO QUEST

 OBJECTIVE:
Match all pairs of identical emojis by flipping cards

 GAMEPLAY:
Click on cards to flip and reveal emojis
Find matching pairs by remembering their positions
Match all pairs to complete the level
Complete within the time limit!
       
 TIME LIMITS:
Level 1: 40 seconds
Level 2: 60 seconds
Level 3: 80 seconds

 LEVELS:
Level 1: Enchanted Forest (3x4 grid - 6 pairs)
Level 2: Under the Sea (4x4 grid - 8 pairs)
Level 3: Steampunk Clockwork (4x5 grid - 10 pairs)

 SCORING:
Fewer moves = Higher score
Faster completion = Bonus points
Complete all levels for maximum score!

 RECORDS:
Your best scores and times are tracked
Try to beat your personal records!

 AUDIO CUES:
Match sound for correct pairs
Miss sound for incorrect pairs

 TIPS:
Pay attention to card positions
Use your memory to recall previous flips
Stay focused and work quickly!

Good luck, Memory Master!
        """

        messagebox.showinfo("Game Instructions", instructions)

    def setup_level_selection(self):
        self.clear_widgets()
        current_theme = LEVEL_THEMES[1] # Use level 1 theme for level selection frame's solid background color

        # Set the main window background to cardback.png
        self.setup_background(self.menu_bg_image_filename, current_theme["bg_color"])

        level_selection_frame = tk.Frame(self.root, bg=current_theme["bg_color"], bd=5, relief="raised")
        level_selection_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_frame = tk.Frame(level_selection_frame, bg=current_theme["bg_color"])
        header_frame.pack(pady=20)

        title = tk.Label(header_frame,
                         text="🎯 SELECT YOUR CHALLENGE LEVEL",
                         font=("Arial", 24, "bold"),
                         bg=current_theme["bg_color"],
                         fg="#f39c12")
        title.pack()

        subtitle = tk.Label(header_frame,
                             text="Each level gets progressively harder!",
                             font=("Arial", 14),
                             bg=current_theme["bg_color"],
                             fg=current_theme["text_color"])
        subtitle.pack(pady=(5, 0))

        # Level buttons
        levels_frame = tk.Frame(level_selection_frame, bg=current_theme["bg_color"])
        levels_frame.pack(pady=30)

        for lvl, data in LEVEL_THEMES.items():
            # Level info
            level_frame = tk.Frame(levels_frame, bg=current_theme["bg_color"])
            level_frame.pack(pady=15)

            # Create horizontal layout for level button and score display
            level_content_frame = tk.Frame(level_frame, bg=current_theme["bg_color"])
            level_content_frame.pack()

            difficulty = ["EASY", "MEDIUM", "HARD"][lvl-1]
            grid_size = f"{data['grid_size'][0]}×{data['grid_size'][1]}"
            time_limit = data['time_limit']

            info_text = f"Level {lvl}: {data['name']}"

            btn = tk.Button(level_content_frame,
                             text=info_text,
                             font=data["font_medium"],
                             bg=data['accent_color'],
                             fg="white",
                             activebackground=self.lighten_color(data['accent_color'], 20),
                             relief="flat",
                             padx=40,
                             pady=15,
                             cursor="hand2",
                             command=lambda l=lvl: (self.play_button_click_sound(), self.start_game(l)))
            btn.pack(side="left", padx=10) # Add padx to separate from records

            # Display highest score and best time for this level (from leaderboard data)
            current_level_records = sorted(self.leaderboard_data[lvl], key=lambda x: (-x[0], x[1])) # Sort by score (desc), then time (asc)
           
            # Leaderboard data format: (score, time_taken, moves, player_name)
            best_score = current_level_records[0][0] if current_level_records else 0
            best_time = current_level_records[0][1] if current_level_records else 0
            best_player = current_level_records[0][3] if current_level_records else "N/A"

            score_text = f"{best_score}" if best_score > 0 else "N/A"
            time_text = f"{best_time}s" if best_time > 0 else "N/A"

            record_text = f"🏆 Best Score: {score_text} ({best_player})\n⚡ Best Time: {time_text}"

            record_label = tk.Label(level_content_frame,
                                     text=record_text,
                                     font=current_theme["font_small"],
                                     bg=current_theme["bg_color"],
                                     fg="#f39c12",
                                     justify="left")
            record_label.pack(side="right", padx=(10, 0))

        # Back button
        back_btn = tk.Button(level_selection_frame,
                               text="⬅️ BACK TO MENU",
                               font=current_theme["font_small"],
                               bg="#95a5a6",
                               fg="white",
                               activebackground="#bdc3c7",
                               relief="flat",
                               padx=20,
                               pady=10,
                               cursor="hand2",
                               command=lambda: (self.play_button_click_sound(), self.setup_main_menu()))
        back_btn.pack(pady=(20, 30))

    def start_game(self, level):
        self.level = level
        theme = LEVEL_THEMES[level]
        self.current_theme = theme # Store current theme for easy access

        self.setup_background(theme["bg_image"], theme["bg_color"]) # Set specific level background

        self.card_back_color = theme["card_back_color"]
        self.accent_color = theme["accent_color"]
        self.text_color = theme["text_color"]
        self.font_large = theme["font_large"]
        self.font_medium = theme["font_medium"]
        self.font_small = theme["font_small"]
        self.time_limit = theme["time_limit"]
        self.time_remaining = self.time_limit

        # Load all card images for this level using Pillow
        self.card_face_images = [] # This will hold ImageTk.PhotoImage objects for card faces

        # Card back image is loaded once in __init__ for main menu, re-load for game if needed or
        # ensure it's loaded consistently for all card backs.
        # It's better to load it here to ensure it uses the specific card_size for the game.
        self.card_back_image_tk = self.load_and_resize_image("cardback.png", *self.card_size)
        if not self.card_back_image_tk: # Fallback if cardback fails to load
            self.card_back_image_tk = ImageTk.PhotoImage(Image.new("RGBA", self.card_size, (0,0,0,0)))


        # Load card face images
        for img_filename in theme["card_images"]:
            tk_image = self.load_and_resize_image(img_filename, *self.card_size)
            if tk_image:
                self.card_face_images.append(tk_image)
            else:
                print(f"Warning: Using blank image for '{img_filename}' due to loading error.")
                blank_img = ImageTk.PhotoImage(Image.new("RGBA", self.card_size, (0,0,0,0)))
                self.card_face_images.append(blank_img)

        self.grid_rows, self.grid_cols = theme["grid_size"]
        self.buttons = []
        self.flipped = []
        self.matched = []
        self.moves = 0
        self.card_map = {} # Maps (row,col) to image index
        self.locked = False
        self.start_time = None
        self.timer_running = False
        self._timer_id = None # To store after() ID for timer
        self._shake_id = None # To store after() ID for shake animation
        self._win_effect_id = None # To store after() ID for win effect

        self.build_game_ui()

    def build_game_ui(self):
        self.clear_widgets()

        # Use a main game frame for all UI elements, placed on top of the background
        self.game_ui_frame = tk.Frame(self.root, bg=self.current_theme["bg_color"], bd=5, relief="raised")
        self.game_ui_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        self.game_ui_frame_original_bg = self.current_theme["bg_color"] # Store original background color

        # Header with level info
        header_frame = tk.Frame(self.game_ui_frame, bg=self.current_theme["bg_color"])
        header_frame.pack(pady=(10, 5))

        level_title = tk.Label(header_frame,
                               text=f"🌟 {self.current_theme['name']} 🌟",
                               font=("Arial", 20, "bold"),
                               bg=self.current_theme["bg_color"],
                               fg=self.current_theme["accent_color"])
        level_title.pack()

        level_info = tk.Label(header_frame,
                              text=f"Level {self.level} - Find all matching pairs within {self.time_limit} seconds!",
                              font=("Arial", 12),
                              bg=self.current_theme["bg_color"],
                              fg=self.current_theme["text_color"])
        level_info.pack()

        # Game stats and controls
        controls_frame = tk.Frame(self.game_ui_frame, bg=self.current_theme["bg_color"])
        controls_frame.pack(pady=(10, 20))

        # Stats frame
        stats_frame = tk.Frame(controls_frame, bg=self.current_theme["bg_color"])
        stats_frame.pack(side="left", padx=20)

        # Player Name label
        self.player_name_label = tk.Label(stats_frame,
                                           text=f"👤: {self.player_name}",
                                           font=self.current_theme["font_medium"],
                                           bg=self.current_theme["bg_color"],
                                           fg=self.current_theme["text_color"])
        self.player_name_label.pack()

        self.move_label = tk.Label(stats_frame,
                                   text="🧠 Moves: 0",
                                   font=self.current_theme["font_medium"],
                                   bg=self.current_theme["bg_color"],
                                   fg=self.current_theme["text_color"])
        self.move_label.pack()

        self.timer_label = tk.Label(stats_frame,
                                   text=f"⏰ Time: {self.time_remaining}s",
                                   font=self.current_theme["font_medium"],
                                   bg=self.current_theme["bg_color"],
                                   fg=self.current_theme["text_color"])
        self.timer_label.pack()

        # Control buttons frame
        buttons_frame = tk.Frame(controls_frame, bg=self.current_theme["bg_color"])
        buttons_frame.pack(side="right", padx=20)

        # Restart button
        restart_btn = tk.Button(buttons_frame,
                                text="🔄 RESTART",
                                font=self.current_theme["font_small"],
                                bg="#f39c12",
                                fg="white",
                                activebackground="#f7dc6f",
                                relief="flat",
                                padx=15,
                                pady=5,
                                cursor="hand2",
                                command=lambda: (self.play_button_click_sound(), self.start_game(self.level)))
        restart_btn.pack(side="left", padx=5)

        # Exit to menu button
        exit_btn = tk.Button(buttons_frame,
                               text="🏠 MENU",
                               font=self.current_theme["font_small"],
                               bg="#e74c3c",
                               fg="white",
                               activebackground="#ec7063",
                               relief="flat",
                               padx=15,
                               pady=5,
                               cursor="hand2",
                               command=lambda: (self.play_button_click_sound(), self.setup_main_menu()))
        exit_btn.pack(side="left", padx=5)

        # Start timer
        self.timer_running = True
        self.start_time = time.time()
        self.update_timer()

        # Game board
        self.game_frame = tk.Frame(self.game_ui_frame, bg=self.current_theme["bg_color"])
        self.game_frame.pack(pady=20)
        self.create_game()

    def create_game(self):
        total_cards = self.grid_rows * self.grid_cols
        pairs = total_cards // 2

        # Ensure we have enough loaded images for the pairs
        if len(self.card_face_images) < pairs:
            messagebox.showwarning("Not Enough Images",
                                   f"Warning: Not enough unique PNG images loaded for Level {self.level}. "
                                   f"Needed {pairs} unique images, but only loaded {len(self.card_face_images)}. "
                                   f"Consider adding more PNG images to your 'images' folder for this level.")
            # Fallback: repeat existing images or use blank if no images at all
            if not self.card_face_images:
                # If no images loaded, fill with blank images
                image_indices = [0] * total_cards # Use an index that will point to a blank image
                blank_img = ImageTk.PhotoImage(Image.new("RGBA", self.card_size, (0,0,0,0)))
                self.card_face_images.append(blank_img)
                self.image_references.append(blank_img) # Keep reference
            else:
                # Repeat available images if not enough unique ones
                image_indices = (list(range(len(self.card_face_images))) * (pairs // len(self.card_face_images) + 1))[:pairs] * 2
        else:
            image_indices = list(range(pairs)) * 2

        random.shuffle(image_indices)

        for r in range(self.grid_rows):
            row = []
            for c in range(self.grid_cols):
                img_idx = image_indices.pop()

                btn = tk.Button(self.game_frame,
                                image=self.card_back_image_tk, # Use the Tkinter PhotoImage for card back
                                bg=self.card_back_color,
                                activebackground=self.lighten_color(self.current_theme["accent_color"], 20),
                                width=self.card_size[0],  # Explicitly set button size for consistent card appearance
                                height=self.card_size[1],
                                relief="raised",
                                bd=3,
                                cursor="hand2",
                                command=lambda r=r, c=c: (self.play_button_click_sound(), self.flip_card(r, c))) # Button click sound for card press
                btn.grid(row=r, column=c, padx=4, pady=4)
                row.append(btn)

                # Store the image index for this card
                self.card_map[(r, c)] = img_idx
            self.buttons.append(row)

    def flip_card(self, row, col):
        # Extract just the (row, col) from already flipped cards for comparison
        flipped_coords = [(r, c) for r, c, _ in self.flipped]

        # Prevent flipping if locked, already flipped in current turn, or already matched
        if self.locked or (row, col) in flipped_coords or (row, col) in self.matched:
            return

        # Lock interactions briefly
        self.locked = True

        button = self.buttons[row][col]
        # Get the actual image object from self.card_face_images based on stored index
        image_to_display = self.card_face_images[self.card_map[(row, col)]]
        button.config(image=image_to_display)

        self.flipped.append((row, col, self.card_map[(row, col)])) # Store (row, col, image_index)

        if len(self.flipped) == 2:
            # Short delay before checking match, allowing both cards to be visible
            self.root.after(400, self.check_match)
        else:
            self.locked = False # Unlock if only one card is flipped

    def check_match(self):
        if len(self.flipped) != 2: # Safety check
            self.locked = False
            return

        (r1, c1, img_idx1) = self.flipped[0]
        (r2, c2, img_idx2) = self.flipped[1]

        self.moves += 1
        self.update_moves_label()

        if img_idx1 == img_idx2:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC) # Success sound
            self.animate_match(r1, c1, r2, c2) # Call the animation for matched cards
            self.matched.extend([(r1, c1), (r2, c2)])
            self.flipped.clear()
            self.check_win()
        else:
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC) # Failure sound
            self._shake_animation_coords = [(r1, c1), (r2, c2)] # Store coords for shake
            self.shake_card_effect(0) # Start shake animation
            # The cards will be hidden within shake_card_effect after the animation
       
        # self.locked is handled in animate_match or shake_card_effect


    def animate_match(self, r1, c1, r2, c2):
        """
        Animates matched cards (e.g., changes their border or visual state)
        and then makes them unclickable.
        """
        button1 = self.buttons[r1][c1]
        button2 = self.buttons[r2][c2]

        # Change appearance for matched cards (e.g., sunken relief, different border color)
        button1.config(relief="sunken", bd=2, bg=self.darken_color(self.current_theme["accent_color"], 10))
        button2.config(relief="sunken", bd=2, bg=self.darken_color(self.current_theme["accent_color"], 10))

        # Disable the buttons so they cannot be clicked again
        button1.config(state="disabled")
        button2.config(state="disabled")

        self.locked = False # Unlock interactions after match animation

    def hide_cards(self, r1, c1, r2, c2):
        self.buttons[r1][c1].config(image=self.card_back_image_tk)
        self.buttons[r2][c2].config(image=self.card_back_image_tk)
        self.flipped.clear()
        self.locked = False

    def shake_card_effect(self, count):
        if count >= 6: # Shake 3 times (0,1,2,3,4,5)
            # Reset position and hide cards after shake
            for r, c in self._shake_animation_coords:
                # Important: Reset grid position correctly. place() overrides grid().
                # Instead of place, we should use grid_configure to adjust padding if shaking via padding.
                # If shaking involves actual pixel shifting, we need to store original positions.
                # For simplicity here, let's assume shaking by changing position relative to its grid cell.
                # For a full reset, if using .place() for shake:
                btn = self.buttons[r][c]
                btn.grid(row=r, column=c, padx=4, pady=4) # Re-apply original grid settings
            self.hide_cards(self._shake_animation_coords[0][0], self._shake_animation_coords[0][1],
                            self._shake_animation_coords[1][0], self._shake_animation_coords[1][1])
            self._shake_animation_coords = [] # Clear coords
            self._shake_id = None
            return

        offset = 5 if count % 2 == 0 else -5
       
        # Apply offset to the two cards that were incorrectly matched
        for r, c in self._shake_animation_coords:
            btn = self.buttons[r][c]
            # Use relx, rely for relative positioning within parent, or absolute x,y if parent is fixed.
            # Using grid_configure for padx is simpler for a shake if not combined with .place()
            # For simplicity with .place() based shake:
            current_x_offset = int(btn.winfo_x() - self.game_frame.winfo_x() - (c * (self.card_size[0] + 8))) # Crude calculation
            current_y_offset = int(btn.winfo_y() - self.game_frame.winfo_y() - (r * (self.card_size[1] + 8))) # Crude calculation

            btn.place(x=(c * (self.card_size[0] + 8)) + offset, y=(r * (self.card_size[1] + 8))) # Recalculate original grid pos + offset

        self._shake_id = self.root.after(70, self.shake_card_effect, count + 1)

    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.time_remaining = max(0, self.time_limit - elapsed_time)
           
            # Color coding for urgency
            if self.time_remaining <= 10:
                color = "#e74c3c"  # Red for last 10 seconds
            elif self.time_remaining <= 20:
                color = "#f39c12"  # Orange for last 20 seconds
            else:
                color = self.current_theme["text_color"] # Default color

            self.timer_label.config(text=f"⏰ Time: {self.time_remaining}s", fg=color)

            if self.time_remaining <= 0:
                self.timer_running = False
                self.game_over(False) # Time's up, player loses
            else:
                self._timer_id = self.root.after(1000, self.update_timer)

    def update_moves_label(self):
        self.move_label.config(text=f"🧠 Moves: {self.moves}")

    def check_win(self):
        total_cards = self.grid_rows * self.grid_cols
        if len(self.matched) == total_cards:
            self.timer_running = False
            self.game_over(True) # Player wins!

    def game_over(self, is_win):
        # Stop any pending timers/animations
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        if self._shake_id:
            self.root.after_cancel(self._shake_id)
            self._shake_id = None
        if hasattr(self, '_win_effect_id') and self._win_effect_id:
            self.root.after_cancel(self._win_effect_id)
            self._win_effect_id = None


        # Only calculate final_time_taken if the game was won
        final_time_taken = self.time_limit - self.time_remaining if is_win else self.time_limit

        if is_win:
            self._trigger_win_effect() # Trigger the visual burst effect on win
            self.calculate_score(final_time_taken)
            self.add_to_leaderboard(self.level, self.total_score, final_time_taken, self.moves, self.player_name)
           
            # Instead of show_congratulations_popup, go directly to leaderboard
            self.root.after(300, lambda: self.show_leaderboard(from_game_over=True, level_just_finished=self.level))
           
        else:
            self.show_game_over_popup()

    def _trigger_win_effect(self):
        """
        Creates a temporary visual burst effect on the game_ui_frame.
        Changes background to a bright color, then fades back to original.
        """
        win_flash_color = "#FFD700" # Gold color for win effect
        flash_duration_ms = 100 # How long each flash state lasts
        num_flashes = 6 # How many times it flashes (on and off for a more prominent burst)

        def flash_step(step_count):
            # Ensure the game_ui_frame still exists before trying to configure it
            if not hasattr(self, 'game_ui_frame') or not self.game_ui_frame.winfo_exists():
                return # Stop if frame no longer exists

            if step_count < num_flashes:
                if step_count % 2 == 0:
                    # Flash on (bright color)
                    self.game_ui_frame.config(bg=win_flash_color)
                else:
                    # Flash off (original color)
                    self.game_ui_frame.config(bg=self.game_ui_frame_original_bg)
                self._win_effect_id = self.root.after(flash_duration_ms, flash_step, step_count + 1)
            else:
                # Ensure it ends on the original background color
                self.game_ui_frame.config(bg=self.game_ui_frame_original_bg)
                self._win_effect_id = None # Clear the ID as effect is complete

        flash_step(0) # Start the flashing sequence


    # This method is no longer called on game win, but kept for reference if needed elsewhere.
    # Its functionality (score, add to leaderboard) is now directly in game_over before show_leaderboard.
    def show_congratulations_popup(self, time_taken, moves):
        # This popup is now deprecated if the user wants to go straight to the leaderboard.
        # If you still want a brief popup with stats AND THEN the leaderboard,
        # you would call this, and then have buttons within this popup lead to leaderboard.
        # For this request, we're skipping this directly to leaderboard.
        pass

    def show_game_over_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("😔 GAME OVER 😔")
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)

        popup_width = 400
        popup_height = 250
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        popup_x = main_x + (main_width // 2) - (popup_width // 2)
        popup_y = main_y + (main_height // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

        current_theme = self.current_theme
        popup.config(bg=current_theme["bg_color"])

        tk.Label(popup, text="TIME'S UP!", font=("Arial", 24, "bold"), fg="#e74c3c", bg=current_theme["bg_color"]).pack(pady=10)
        tk.Label(popup, text="You ran out of time! Better luck next time.", font=("Arial", 14), fg=current_theme["text_color"], bg=current_theme["bg_color"]).pack(pady=5)
        tk.Label(popup, text=f"Your Score: {self.total_score}", font=("Arial", 16, "bold"), fg=current_theme["accent_color"], bg=current_theme["bg_color"]).pack(pady=10)

        button_frame = tk.Frame(popup, bg=current_theme["bg_color"])
        button_frame.pack(pady=15)

        retry_btn = tk.Button(button_frame, text="🔄 TRY AGAIN", command=lambda: (self.play_button_click_sound(), popup.destroy(), self.start_game(self.level)),
                              font=("Arial", 14), bg="#f39c12", fg="white", activebackground="#f7dc6f", relief="flat", padx=15, pady=8, cursor="hand2")
        retry_btn.pack(side="left", padx=10)

        menu_btn = tk.Button(button_frame, text="🏠 MAIN MENU", command=lambda: (self.play_button_click_sound(), popup.destroy(), self.setup_main_menu()),
                              font=("Arial", 14), bg="#3498db", fg="white", activebackground="#5dade2", relief="flat", padx=15, pady=8, cursor="hand2")
        menu_btn.pack(side="left", padx=10)

        popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), self.setup_main_menu()))

    def calculate_score(self, time_taken):
        # Base score (e.g., 1000 points per level)
        base_score = 1000
       
        # Time bonus: Faster completion yields more points
        # Max time bonus if completed instantly, 0 if just made it
        time_bonus_per_sec = 10
        time_bonus = self.time_remaining * time_bonus_per_sec # time_remaining is what's left

        # Move penalty: More moves, less score
        move_penalty_per_move = 50
        move_penalty = self.moves * move_penalty_per_move

        # Ensure score doesn't go below 0
        self.total_score = max(0, base_score + time_bonus - move_penalty)
        return self.total_score

    def add_to_leaderboard(self, level, score, time_taken, moves, player_name):
        self.leaderboard_data[level].append((score, time_taken, moves, player_name))
        self.leaderboard_data[level].sort(key=lambda x: (-x[0], x[1])) # Sort by score (desc), then time (asc)
        self.leaderboard_data[level] = self.leaderboard_data[level][:5] # Keep top 5 records
        self.save_leaderboard() # Save to file after updating

    def load_leaderboard(self):
        try:
            with open("leaderboard.txt", "r") as f:
                for line in f:
                    try:
                        level, score, time_taken, moves, player_name = line.strip().split(',')
                        self.leaderboard_data[int(level)].append((int(score), int(time_taken), int(moves), player_name))
                    except ValueError as e:
                        print(f"Skipping malformed leaderboard entry: {line.strip()} ({e})")
                # Ensure each level's data is sorted after loading
                for lvl in self.leaderboard_data:
                    self.leaderboard_data[lvl].sort(key=lambda x: (-x[0], x[1]))
        except FileNotFoundError:
            pass # File will be created on first save

    def save_leaderboard(self):
        try:
            with open("leaderboard.txt", "w") as f:
                for level, records in self.leaderboard_data.items():
                    for score, time_taken, moves, player_name in records:
                        f.write(f"{level},{score},{time_taken},{moves},{player_name}\n")
        except Exception as e:
            messagebox.showerror("Leaderboard Save Error", f"Error saving leaderboard: {e}")
            print(f"Error saving leaderboard: {e}")

    def show_leaderboard(self, from_game_over=False, level_just_finished=None):
        self.clear_widgets()
        current_theme = LEVEL_THEMES[1] # Use level 1 theme for menu background
        self.setup_background(self.menu_bg_image_filename, current_theme["bg_color"])

        leaderboard_frame = tk.Frame(self.root, bg=current_theme["bg_color"], bd=5, relief="raised")
        leaderboard_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

        tk.Label(leaderboard_frame, text="🏆 NEURO QUEST LEADERBOARD 🏆", font=("Arial Black", 28, "bold"), fg="#f39c12", bg=current_theme["bg_color"]).pack(pady=(20, 10))
       
        # New text to congratulate the player when coming from a win
        if from_game_over and level_just_finished:
            win_message = f"🎉 CONGRATULATIONS, {self.player_name}! You completed Level {level_just_finished}!"
            tk.Label(leaderboard_frame, text=win_message, font=("Arial", 16, "bold"), fg="#FFD700", bg=current_theme["bg_color"]).pack(pady=(0, 5))
            tk.Label(leaderboard_frame, text=f"Your Score: {self.total_score} | Moves: {self.moves} | Time: {self.time_limit - self.time_remaining}s",
                     font=("Arial", 14), fg=current_theme["text_color"], bg=current_theme["bg_color"]).pack(pady=(0, 10))
        else:
            tk.Label(leaderboard_frame, text="Top Players by Level!", font=("Arial", 16, "italic"), fg=current_theme["text_color"], bg=current_theme["bg_color"]).pack(pady=(0, 20))

        # Create a notebook (tabbed interface) for levels
        notebook = ttk.Notebook(leaderboard_frame)
        notebook.pack(expand=True, fill="both", padx=20, pady=10)
        notebook.bind("<<NotebookTabChanged>>", self.play_button_click_sound_on_tab_change)

        # --- Apply a basic style to the notebook tabs for better appearance ---
        style = ttk.Style()
        style.theme_use('clam') # Use 'clam' theme for more customization
        # Configure the 'TNotebook' style (the overall notebook background)
        style.configure("TNotebook", background=current_theme["bg_color"], borderwidth=0)
       
        # Configure the 'TNotebook.Tab' style (unselected tabs)
        # Using a slightly lighter, but distinct, background for unselected tabs
        tab_unselected_bg = self.lighten_color(current_theme["bg_color"], 20) # Lighten more for better contrast
        tab_unselected_fg = current_theme["text_color"] # Keep light text
       
        style.configure("TNotebook.Tab",
                        background=tab_unselected_bg,
                        foreground=tab_unselected_fg,
                        font=("Arial", 12, "bold"), # Increased font size for better visibility
                        padding=[15, 8]) # Increased padding for larger tabs
       
        # Configure the 'TNotebook.Tab' for when it is selected
        style.map("TNotebook.Tab",
                  background=[("selected", current_theme["accent_color"])], # Accent color for selected tab
                  foreground=[("selected", "white")]) # White text for selected tab


        # Define column widths, alignments, and padding
        # (Text for header, width, anchor, padx_tuple=(left_pad, right_pad))
        col_specs = [
            ("Rank", 4, "e", (2, 2)),       # Rank (right-aligned, small padding)
            ("Score", 7, "e", (2, 2)),      # Score (right-aligned, small padding)
            ("Time (s)", 10, "e", (2, 2)),  # Time (right-aligned, small padding)
            ("Moves", 7, "e", (2, 10)),     # Moves (right-aligned, more padding on right to separate from Player)
            ("Player", 20, "w", (10, 2))    # Player (left-aligned, more padding on left to separate from Moves)
        ]

        for lvl in sorted(LEVEL_THEMES.keys()):
            tab_frame = tk.Frame(notebook, bg=current_theme["bg_color"])
            notebook.add(tab_frame, text=f"Level {lvl}") # Shorter tab text

            # Leaderboard header for each level's tab using grid
            header_row_frame = tk.Frame(tab_frame, bg=current_theme["bg_color"])
            header_row_frame.pack(fill="x", pady=(10, 5)) # Pack the header row frame

            for i, (text, width, anchor, padx_tuple) in enumerate(col_specs):
                header_label = tk.Label(header_row_frame, text=text, font=("Arial", 12, "bold"),
                                         fg=LEVEL_THEMES[lvl]['accent_color'], bg=current_theme["bg_color"],
                                         width=width, anchor=anchor)
                header_label.grid(row=0, column=i, padx=padx_tuple, sticky="ew") # Use padx_tuple
                header_row_frame.grid_columnconfigure(i, weight=1) # Allow columns to expand proportionately

            tk.Frame(tab_frame, height=2, bg=LEVEL_THEMES[lvl]['accent_color']).pack(fill="x", padx=10, pady=(0, 10)) # Separator

            level_records = sorted(self.leaderboard_data[lvl], key=lambda x: (-x[0], x[1])) # Sort by score (desc), then time (asc)

            if not level_records:
                tk.Label(tab_frame, text="No records yet for this level!", font=("Arial", 12), fg=current_theme["text_color"], bg=current_theme["bg_color"]).pack(pady=20)
            else:
                for i, record_tuple in enumerate(level_records):
                    score, time_taken, moves, player_name = record_tuple
                   
                    is_current_player_record = (player_name == self.player_name and
                                                score == self.total_score and
                                                (time_taken == (self.time_limit - self.time_remaining) if self.time_remaining is not None else True) and
                                                (moves == self.moves if self.moves is not None else True))
                   
                    # Highlight the current player's newly achieved record
                    # This logic needs to be a bit more robust if multiple entries can have same name/score
                    # For simplicity, we check if it matches the latest game's stats.
                   
                    record_row_frame = tk.Frame(tab_frame, bg=current_theme["bg_color"])
                    record_row_frame.pack(fill="x", pady=2) # Pack each record row frame

                    for j, (header_text, width, anchor, padx_tuple) in enumerate(col_specs): # Get padx_tuple from col_specs
                        # Determine the text to display for the current column
                        display_text = ""
                        if j == 0: # Rank
                            display_text = f"{i+1}."
                        elif j == 1: # Score
                            display_text = f"{score}"
                        elif j == 2: # Time
                            display_text = f"{time_taken}s"
                        elif j == 3: # Moves
                            display_text = f"{moves}"
                        elif j == 4: # Player
                            # Truncate player name if too long for the column width, accounting for "..."
                            max_name_len = width * 2 # Approximate chars based on width units
                            display_text = (player_name[:max_name_len] + "..." if len(player_name) > max_name_len + 3 else player_name)

                        record_label = tk.Label(record_row_frame,
                                                text=display_text,
                                                font=("Consolas", 12), # Monospace font for alignment
                                                fg="#f4e4bc" if not is_current_player_record else "#FFD700", # Gold for new best
                                                bg=current_theme["bg_color"],
                                                width=width,
                                                anchor=anchor)
                        record_label.grid(row=0, column=j, padx=padx_tuple, sticky="ew") # Use padx_tuple
                        record_row_frame.grid_columnconfigure(j, weight=1) # Allow columns to expand proportionately


        # Select the tab for the level just finished, if coming from game over
        if from_game_over and level_just_finished is not None:
            # The notebook's select method expects a 0-based index
            # Check if the level_just_finished is a valid index for the notebook tabs
            if 0 <= (level_just_finished - 1) < len(LEVEL_THEMES):
                notebook.select(level_just_finished - 1) # Notebook indices are 0-based

        # Back to menu button
        back_btn = tk.Button(leaderboard_frame,
                               text="⬅️ BACK TO MENU",
                               font=current_theme["font_medium"],
                               width=20,
                               bg="#95a5a6",
                               fg="white",
                               activebackground="#bdc3c7",
                               relief="flat",
                               padx=20,
                               pady=10,
                               cursor="hand2",
                               command=lambda: (self.play_button_click_sound(), self.setup_main_menu()))
        back_btn.pack(pady=(11, 10))

        # Add a "Play Next Level" button if applicable
        if from_game_over and self.level < len(LEVEL_THEMES):
            next_level_btn = tk.Button(leaderboard_frame, text="🚀 PLAY NEXT LEVEL",
                                        command=lambda: (self.play_button_click_sound(), self.start_game(self.level + 1)),
                                        font=("Arial", 14, "bold"), bg="#27ae60", fg="white", activebackground="#2ecc71",
                                        relief="flat", width=20, padx=20, pady=10, cursor="hand2")
            next_level_btn.pack(pady=(0, 20)) # Place it below "Back to menu"


    def lighten_color(self, hex_color, factor):
        """
        Lightens a hex color by a given factor (percentage).
        factor should be between 0 and 100.
        """
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
       
        lightened_rgb = [min(255, c + int(255 * factor / 100)) for c in rgb]
        return '#%02x%02x%02x' % tuple(lightened_rgb)

    def darken_color(self, hex_color, factor):
        """
        Darkens a hex color by a given factor (percentage).
        factor should be between 0 and 100.
        """
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
       
        darkened_rgb = [max(0, c - int(255 * factor / 100)) for c in rgb]
        return '#%02x%02x%02x' % tuple(darkened_rgb)

    def exit_game(self):
        if messagebox.askyesno("Exit Game", "Are you sure you want to exit Neuro Quest?"):
            self.root.destroy()

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    game = NeuroQuestGame(root)
    root.mainloop()
