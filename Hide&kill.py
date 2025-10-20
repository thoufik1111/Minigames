import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk # Required for image handling
import random
import time

class HideAndKillGame(tk.Tk):
    """
    A multi-player Hide & Kill game with a fixed room layout, killer animation,
    and a visual killer sprite that moves between rooms.
    """
    ROOM_COUNT = 8
    MAX_ROUNDS = 10
    POINTS_LOST = 1
    CANVAS_SIZE = 600 # Increased canvas size
    ROOM_COLORS = "#E0E0E0" # Light grey for unsearched rooms
    BG_COLOR = "#f0f0f0"
    WALL_COLOR = "#6D4C41" # Brown for walls
    SEARCHED_COLOR = "#FF9800" # Orange during search
    KILLED_COLOR = "#F44336" # Red after search
    SAFE_COLOR = "#4CAF50" # Green for the safe room
    
    # Updated Fixed positions (x1, y1, x2, y2) for 8 rooms in a larger house layout
    FIXED_LAYOUT = {
        1: (50, 50, 200, 200),   # Top-Left
        2: (225, 50, 375, 200),  # Top-Center
        3: (400, 50, 550, 200),  # Top-Right
        4: (50, 225, 200, 375),  # Mid-Left
        5: (225, 225, 375, 375), # Center/Hallway
        6: (400, 225, 550, 375), # Mid-Right
        7: (50, 400, 200, 550),  # Bot-Left
        8: (400, 400, 550, 550)  # Bot-Right
    }

    # Connections for drawing doors
    ROOM_CONNECTIONS = {
        1: [2, 4], 2: [1, 3, 5], 3: [2, 6],
        4: [1, 5, 7], 5: [2, 4, 6, 8], 6: [3, 5],
        7: [4, 8], 8: [5, 7]
    }

    def __init__(self):
        """Initializes the main application window and game state."""
        super().__init__()
        self.title("Hide & Kill Game")
        self.geometry("1000x700") # Adjusted window size
        self.config(bg=self.BG_COLOR)
        
        # Game State Variables
        self.player_names = []
        self.scores = {}
        self.current_round = 0
        self.room_canvas_ids = {} # Stores Canvas item IDs for coloring
        self.current_selections = {} # Stores player choices for the current round
        self.searched_rooms_sequence = [] # Order in which the killer checks rooms
        self.animation_step = 0
        self.killer_img_ref = None # Keep a reference to prevent garbage collection
        self.killer_sprite_id = None # Canvas ID for killer image
        
        # UI Elements
        self.main_frame = None
        self.canvas = None
        self.round_label = None
        self.scoreboard_label = None
        self.player_room_entries = {}
        self.lock_in_button = None
        self.result_text = None
        
        # Load killer image
        try:
            original_killer_img = Image.open("killer.jpg") # Make sure "killer.png" is in the same directory
            self.killer_img = ImageTk.PhotoImage(original_killer_img.resize((60, 60))) # Resize as needed
        except FileNotFoundError:
            messagebox.showwarning("Image Not Found", "killer.png not found. Killer image won't be displayed.")
            self.killer_img = None
        except Exception as e:
            messagebox.showwarning("Image Error", f"Error loading killer.png: {e}. Killer image won't be displayed.")
            self.killer_img = None
            
        self.show_player_setup()

    # --- UI Setup ---

    def show_player_setup(self):
        """Displays the initial setup screen for selecting the number of players."""
        if self.main_frame:
            self.main_frame.destroy()
            
        self.main_frame = tk.Frame(self, padx=40, pady=40, bg=self.BG_COLOR)
        self.main_frame.pack(expand=True)
        
        tk.Label(self.main_frame, text="Hide & Kill Setup", font=("Inter", 28, "bold"), bg=self.BG_COLOR, fg="#333333").pack(pady=15)
        tk.Label(self.main_frame, text="Enter Player Names (2 to 6):", font=("Inter", 16), bg=self.BG_COLOR, fg="#555555").pack(pady=15)
        
        self.setup_entries = []
        for i in range(6):
            frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
            frame.pack(pady=7)
            tk.Label(frame, text=f"Player {i+1}:", width=10, anchor="w", font=("Inter", 12), bg=self.BG_COLOR, fg="#333333").pack(side="left")
            entry = tk.Entry(frame, width=25, font=("Inter", 12), relief=tk.FLAT, bd=1, highlightbackground="#ccc", highlightthickness=1)
            entry.pack(side="left")
            self.setup_entries.append(entry)
            
            if i < 2: entry.insert(0, f"Player {i+1}") 

        start_button = tk.Button(self.main_frame, text="START 10-ROUND GAME", command=self.start_game, 
                                 font=("Inter", 16, "bold"), bg="#1E88E5", fg="white", 
                                 activebackground="#1565C0", activeforeground="white",
                                 relief=tk.FLAT, padx=25, pady=12, bd=0, cursor="hand2")
        start_button.pack(pady=40)
        
    def start_game(self):
        """Validates player names, initializes scores, and moves to the main game screen."""
        self.player_names = [e.get().strip() for e in self.setup_entries if e.get().strip()]
        
        if len(self.player_names) < 2 or len(self.player_names) > 6:
            messagebox.showerror("Error", "Please enter between 2 and 6 player names.")
            return

        self.scores = {name: 10 for name in self.player_names} # Start with 10 points
        self.current_round = 1
        
        self.main_frame.destroy()
        self.create_main_game_ui()
        self.draw_rooms()
        self.update_scoreboard()
        self.start_new_round()

    def create_main_game_ui(self):
        """Sets up the main game interface with the canvas and control panel."""
        self.main_frame = tk.Frame(self, bg=self.BG_COLOR)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left Side: Canvas
        canvas_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        canvas_frame.pack(side="left", padx=20)
        
        tk.Label(canvas_frame, text="House Layout (Rooms 1-8)", font=("Inter", 16, "italic"), bg=self.BG_COLOR, fg="#555555").pack(pady=10)
        self.canvas = tk.Canvas(canvas_frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, 
                                bg=self.WALL_COLOR, highlightthickness=3, highlightbackground="#333333")
        self.canvas.pack()
        
        # Right Side: Controls and Scoreboard
        control_panel = tk.Frame(self.main_frame, bg=self.BG_COLOR, padx=15, pady=15, width=300)
        control_panel.pack(side="right", fill="both", expand=True)
        control_panel.pack_propagate(False) # Prevent frame from shrinking to fit content

        # Scoreboard and Round
        self.round_label = tk.Label(control_panel, text="", font=("Inter", 18, "bold"), bg=self.BG_COLOR, fg="#333333")
        self.round_label.pack(pady=(0, 15))
        
        self.scoreboard_label = tk.Label(control_panel, text="", font=("Inter", 13), justify=tk.LEFT, bg=self.BG_COLOR, fg="#555555")
        self.scoreboard_label.pack(pady=(0, 25), fill="x")
        
        # Control Panel: Player Room Selection
        tk.Label(control_panel, text="Choose Your Room (1-8):", font=("Inter", 15, "bold"), bg=self.BG_COLOR, fg="#333333").pack(pady=10)
        
        input_grid = tk.Frame(control_panel, bg=self.BG_COLOR)
        input_grid.pack(fill="x")
        
        self.player_room_entries = {}
        for i, name in enumerate(self.player_names):
            frame = tk.Frame(input_grid, bg=self.BG_COLOR)
            frame.pack(pady=6, fill='x')
            
            tk.Label(frame, text=f"{name}:", width=12, anchor="w", font=("Inter", 12), bg=self.BG_COLOR, fg="#333333").pack(side="left")
            entry = tk.Entry(frame, width=5, font=("Inter", 12), justify="center", relief=tk.SOLID, bd=1, highlightbackground="#ccc", highlightthickness=1)
            entry.pack(side="left", padx=5)
            self.player_room_entries[name] = entry

        self.lock_in_button = tk.Button(control_panel, text="LOCK IN CHOICES", command=self.process_round, 
                                        font=("Inter", 14, "bold"), bg="#FF5722", fg="white", 
                                        activebackground="#e64a19", activeforeground="white",
                                        relief=tk.FLAT, padx=20, pady=10, bd=0, cursor="hand2")
        self.lock_in_button.pack(pady=25)
        
        self.result_text = tk.Label(control_panel, text="", font=("Inter", 13), wraplength=280, justify=tk.CENTER, bg=self.BG_COLOR, fg="#777777")
        self.result_text.pack(pady=10, fill="x")

    # --- Game Mechanics & Drawing ---

    def draw_rooms(self):
        """Draws the fixed room layout and doors on the canvas."""
        self.canvas.delete("all")
        self.room_canvas_ids = {}
        
        for room_id, (x1, y1, x2, y2) in self.FIXED_LAYOUT.items():
            
            # Draw the room rectangle
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                   fill=self.ROOM_COLORS, outline=self.WALL_COLOR, width=3, 
                                                   tags=f"room_{room_id}")
            self.room_canvas_ids[room_id] = rect_id
            
            # Draw the room number
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            self.canvas.create_text(x_center, y_center, 
                                    text=str(room_id), font=("Inter", 32, "bold"), 
                                    fill="#333333", tags=f"label_{room_id}")
        
        # Draw doors using connections
        door_width = 8
        for room_id, connections in self.ROOM_CONNECTIONS.items():
            x1, y1, x2, y2 = self.FIXED_LAYOUT[room_id]
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            for connected_room_id in connections:
                cx1, cy1, cx2, cy2 = self.FIXED_LAYOUT[connected_room_id]
                ccenter_x = (cx1 + cx2) / 2
                ccenter_y = (cy1 + cy2) / 2

                # Check if connection is horizontal or vertical
                if abs(center_x - ccenter_x) > abs(center_y - ccenter_y): # Horizontal connection
                    if ccenter_x > center_x: # Connected room is to the right
                        self.canvas.create_line(x2, center_y - door_width, x2, center_y + door_width, fill=self.WALL_COLOR, width=door_width)
                    else: # Connected room is to the left
                        self.canvas.create_line(x1, center_y - door_width, x1, center_y + door_width, fill=self.WALL_COLOR, width=door_width)
                else: # Vertical connection
                    if ccenter_y > center_y: # Connected room is below
                        self.canvas.create_line(center_x - door_width, y2, center_x + door_width, y2, fill=self.WALL_COLOR, width=door_width)
                    else: # Connected room is above
                        self.canvas.create_line(center_x - door_width, y1, center_x + door_width, y1, fill=self.WALL_COLOR, width=door_width)

        # Place killer sprite at a starting point (e.g., center of room 5 or outside)
        if self.killer_img:
            # You can choose a different starting point, e.g., slightly off-canvas or in a central room.
            # Here, starting at room 5's center
            cx, cy = self.get_room_center(5) 
            self.killer_sprite_id = self.canvas.create_image(cx, cy, image=self.killer_img, tags="killer_sprite")
            self.canvas.itemconfigure(self.killer_sprite_id, state="hidden") # Hide initially

    def get_room_center(self, room_id):
        """Calculates the center (x, y) coordinates of a given room."""
        x1, y1, x2, y2 = self.FIXED_LAYOUT[room_id]
        return (x1 + x2) / 2, (y1 + y2) / 2

    def update_scoreboard(self):
        """Updates the scoreboard display with current scores and round number."""
        self.round_label.config(text=f"Round {self.current_round} / {self.MAX_ROUNDS}")
        
        sorted_scores = sorted(self.scores.items(), key=lambda item: item[1], reverse=True)
        
        score_text = "CURRENT STANDINGS:\n"
        for name, score in sorted_scores:
            score_text += f"{name}: {score} Points\n"
        
        self.scoreboard_label.config(text=score_text)
        
    def process_round(self):
        """Gets player choices and initiates the Killer animation."""
        
        selections = {}
        valid_round = True
        
        for name, entry in self.player_room_entries.items():
            try:
                room_choice = int(entry.get())
                if 1 <= room_choice <= self.ROOM_COUNT:
                    selections[name] = room_choice
                else:
                    messagebox.showerror("Invalid Input", f"{name}: Room must be between 1 and {self.ROOM_COUNT}.")
                    valid_round = False
                    break
            except ValueError:
                messagebox.showerror("Invalid Input", f"{name}: Please enter a valid number for your room choice.")
                valid_round = False
                break

        if not valid_round:
            return

        self.current_selections = selections
        self.lock_in_button.config(state=tk.DISABLED, text="KILLER IS SEARCHING...")
        self.result_text.config(text="Choices locked in. Killer approaching...", fg="#FF5722")
        
        all_rooms = list(range(1, self.ROOM_COUNT + 1))
        self.safe_room = random.choice(all_rooms) 
        
        self.searched_rooms_sequence = [r for r in all_rooms if r != self.safe_room]
        random.shuffle(self.searched_rooms_sequence)
        
        self.animation_step = 0
        
        # Show killer sprite at the first room to be searched
        if self.killer_img and self.searched_rooms_sequence:
            initial_room_id = self.searched_rooms_sequence[0]
            cx, cy = self.get_room_center(initial_room_id)
            self.canvas.coords(self.killer_sprite_id, cx, cy)
            self.canvas.itemconfigure(self.killer_sprite_id, state="normal") # Make visible
        
        self.animate_killer_search()

    def animate_killer_search(self):
        """Iteratively highlights a room as the Killer searches it and moves the killer sprite."""
        if self.animation_step < len(self.searched_rooms_sequence):
            room_id = self.searched_rooms_sequence[self.animation_step]
            rect_id = self.room_canvas_ids.get(room_id)

            # Move killer sprite to current room's center
            if self.killer_img:
                cx, cy = self.get_room_center(room_id)
                self.canvas.coords(self.killer_sprite_id, cx, cy)

            self.canvas.itemconfig(rect_id, fill=self.SEARCHED_COLOR, outline="black", width=4)
            self.update_idletasks() # Force update to show color change
            
            self.result_text.config(text=f"Killer is searching Room {room_id}...", fg="#FF9800")
            
            # Briefly hold orange, then change to red
            self.after(600, lambda: self.canvas.itemconfig(rect_id, fill=self.KILLED_COLOR, outline="red", width=4))
            
            self.animation_step += 1
            self.after(1500, self.animate_killer_search) # Wait for 1.5s before next room
        else:
            # Animation finished, hide killer sprite
            if self.killer_img:
                self.canvas.itemconfigure(self.killer_sprite_id, state="hidden")
            self.after(500, self.show_round_result)

    def show_round_result(self, final_show=True):
        """Reveals the safe room and finalizes the scores for the round."""
        
        # 1. Highlight the Safe Room (The unsearched room)
        safe_rect_id = self.room_canvas_ids.get(self.safe_room)
        if safe_rect_id:
            self.canvas.itemconfig(safe_rect_id, fill=self.SAFE_COLOR, outline="green", width=4)
        
        # 2. Calculate point loss
        killed_players = []
        for name, choice in self.current_selections.items():
            if choice != self.safe_room:
                self.scores[name] -= self.POINTS_LOST
                killed_players.append(name)
        
        # 3. Display Results
        if not killed_players:
            result_message = "NO ONE WAS CAUGHT! You all chose wisely."
        else:
            result_message = f"CAUGHT: {', '.join(killed_players)} (Lost {self.POINTS_LOST} Point{'s' if self.POINTS_LOST > 1 else ''} each)"
        
        result_message += f"\nTHE SAFE ROOM WAS ROOM {self.safe_room}!"
        
        self.result_text.config(text=result_message, fg="#000000", font=("Inter", 14, "bold"))
        
        # 4. Schedule the start of the next round
        self.update_scoreboard()
        self.after(4000, self.next_round_or_end) # 4 second delay to appreciate results

    def start_new_round(self):
        """Resets the UI for a new round."""
        self.draw_rooms() # Reset all room colors
        self.update_scoreboard()
        self.result_text.config(text="Place your bets and choose a room to hide!", fg="#777777")
        self.current_selections = {}
        
        for entry in self.player_room_entries.values():
            entry.delete(0, tk.END)
            
        self.lock_in_button.config(state=tk.NORMAL, text="LOCK IN CHOICES")

    def next_round_or_end(self):
        """Determines whether to start a new round or end the game."""
        self.current_round += 1
        
        if self.current_round <= self.MAX_ROUNDS:
            self.start_new_round()
        else:
            self.end_game()

    def end_game(self):
        """Calculates and displays the final game winner."""
        final_scores = self.scores
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
        
        winner_score = sorted_scores[0][1]
        winners = [name for name, score in final_scores.items() if score == winner_score]

        self.canvas.delete("all")
        self.round_label.config(text="GAME OVER", fg="#CC0000")

        if len(winners) == 1:
            win_message = f"🏆 WINNER: {winners[0]} 🏆"
        else:
            win_message = f"Tie Game! Co-Winners: {', '.join(winners)}"
        
        self.result_text.config(text=win_message + f"\nFinal Score: {winner_score} points!", 
                                font=("Inter", 17, "bold"), fg="#008CBA")
        
        self.scoreboard_label.config(text="\nFinal Standings:\n" + "\n".join([f"{name}: {score} pts" for name, score in sorted_scores]), 
                                     font=("Inter", 14), fg="#333333")
        
        self.lock_in_button.config(state=tk.DISABLED, text="GAME FINISHED")
        
        restart_button = tk.Button(self.main_frame, text="Play Again", command=self.show_player_setup, 
                                 font=("Inter", 13), bg="#5cb85c", fg="white", 
                                 activebackground="#4cae4c", activeforeground="white",
                                 relief=tk.FLAT, padx=15, pady=8, bd=0, cursor="hand2")
        restart_button.pack(pady=15)


if __name__ == "__main__":
    game = HideAndKillGame()
    game.mainloop()
