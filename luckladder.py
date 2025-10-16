# luck_ladder_gui_simple.py
# Luck Ladder — Simplified GUI with Mode selection (1 = vs Computer, 2 = 2-player hotseat)
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext

# ---------- Configuration ----------
NUM_PATHS = 5
PATH_LENGTH = 20
DICE_SIDES = 6

CHOICE_TILE_RATIO = 0.35
QUIZ_TILE_RATIO   = 0.20
GAMBLE_TILE_RATIO = 0.20
PUZZLE_TILE_RATIO = 0.25

BAD_NUMBERS_PER_TILE = 4
QUIZ_FORWARD = 5
QUIZ_BACK = 3
GAMBLE_MULTIPLIER = 2
PUZZLE_FORWARD = 4
PUZZLE_BACK = 2

COMP_QUIZ_PROB = 0.55
COMP_PUZZLE_PROB = 0.85
COMP_ROUTE_ACCEPT_PROB = 0.5

QUIZ_BANK = [
    ("Capital of Australia?", "canberra"),
    ("What is 2 + 2?", "4"),
    ("Largest planet in the solar system?", "jupiter"),
    ("What color do you get by mixing blue and yellow?", "green"),
    ("Who wrote 'Romeo and Juliet'?", "shakespeare"),
    ("Capital of India?", "new delhi"),
    ("H2O is chemical formula of what?", "water"),
    ("What is the square root of 9?", "3"),
    ("How many continents are there?", "7"),
    ("Which animal is known as king of the jungle?", "lion"),
    ("Which country has the Eiffel Tower?", "france"),
]

# ---------- Game structures ----------
class Tile:
    def __init__(self, typ, **kwargs):
        self.type = typ  # 'choice','quiz','route','gamble','puzzle'
        self.bad_numbers = kwargs.get('bad_numbers', set())
        self.quiz = kwargs.get('quiz', None)
        self.route_id = kwargs.get('route_id', None)
    def describe_short(self):
        return self.type.upper()

class Path:
    def __init__(self, length, index):
        self.index = index
        self.tiles = []
        route_pos = random.randint(2, max(2, length - 1))
        for i in range(length):
            if i == route_pos:
                self.tiles.append(Tile('route', route_id=i))
                continue
            r = random.random()
            if r < CHOICE_TILE_RATIO:
                bad = set(random.sample(range(1, 11), BAD_NUMBERS_PER_TILE))
                self.tiles.append(Tile('choice', bad_numbers=bad))
            elif r < CHOICE_TILE_RATIO + QUIZ_TILE_RATIO:
                q = random.choice(QUIZ_BANK)
                self.tiles.append(Tile('quiz', quiz=q))
            elif r < CHOICE_TILE_RATIO + QUIZ_TILE_RATIO + GAMBLE_TILE_RATIO:
                self.tiles.append(Tile('gamble'))
            else:
                self.tiles.append(Tile('puzzle'))

class LuckLadder:
    def __init__(self):
        self.reset_all()
    def reset_all(self):
        self.paths = [Path(PATH_LENGTH, i) for i in range(NUM_PATHS)]
        self.p1_pos = 0
        self.p2_pos = 0           # used for computer or player2
        self.p1_path = None
        self.p2_path = None
    def roll(self): return random.randint(1, DICE_SIDES)
    def winner(self):
        if self.p1_pos >= PATH_LENGTH and self.p2_pos >= PATH_LENGTH: return 'tie'
        if self.p1_pos >= PATH_LENGTH: return 'player1'
        if self.p2_pos >= PATH_LENGTH: return 'player2'
        return None

# ---------- GUI ----------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Luck Ladder — Simple (Mode: vs Computer / 2-player)")
        self.game = LuckLadder()
        self.mode = tk.IntVar(value=1)  # 1 = vs Computer, 2 = two-player
        self.current_turn = 'p1'  # 'p1' or 'p2' during play
        self._build_ui()
        self._refresh_ui()

    def _build_ui(self):
        pad = 8
        main = ttk.Frame(self.root, padding=pad)
        main.grid(sticky="nsew")

        # Top controls: mode selector, path pick(s), start, reset, info
        top = ttk.Frame(main)
        top.grid(row=0, column=0, sticky="we")

        ttk.Label(top, text="Mode:").grid(row=0, column=0, sticky="w")
        mode_frame = ttk.Frame(top)
        mode_frame.grid(row=0, column=1, sticky="w", padx=(6,12))
        ttk.Radiobutton(mode_frame, text="1 — vs Computer", variable=self.mode, value=1, command=self._on_mode_change).grid(row=0, column=0)
        ttk.Radiobutton(mode_frame, text="2 — 2 Players (hotseat)", variable=self.mode, value=2, command=self._on_mode_change).grid(row=0, column=1)

        ttk.Label(top, text="Player1 Path:").grid(row=0, column=2, sticky="w")
        self.p1_path_var = tk.StringVar(value="1")
        self.p1_path_combo = ttk.Combobox(top, textvariable=self.p1_path_var, values=[str(i+1) for i in range(NUM_PATHS)], width=4, state='readonly')
        self.p1_path_combo.grid(row=0, column=3, padx=(6,12))

        ttk.Label(top, text="Player2 Path:").grid(row=0, column=4, sticky="w")
        self.p2_path_var = tk.StringVar(value="2")
        self.p2_path_combo = ttk.Combobox(top, textvariable=self.p2_path_var, values=[str(i+1) for i in range(NUM_PATHS)], width=4, state='readonly')
        self.p2_path_combo.grid(row=0, column=5, padx=(6,12))

        self.start_btn = ttk.Button(top, text="Start (lock)", command=self.start_game)
        self.start_btn.grid(row=0, column=6, padx=6)
        self.reset_btn = ttk.Button(top, text="Reset", command=self.reset_game)
        self.reset_btn.grid(row=0, column=7, padx=6)

        self.challenges_btn = ttk.Button(top, text="Challenges Info", command=self.show_challenges_info)
        self.challenges_btn.grid(row=0, column=8, padx=6)
        self.pathinfo_btn = ttk.Button(top, text="Path Info", command=self.show_path_info)
        self.pathinfo_btn.grid(row=0, column=9, padx=6)

        # Middle: status + roll
        mid = ttk.Frame(main, padding=(0,8))
        mid.grid(row=1, column=0, sticky="we")
        self.status_lbl = ttk.Label(mid, text="Positions — P1: 0 | P2/Comp: 0", font=('Segoe UI', 10, 'bold'))
        self.status_lbl.grid(row=0, column=0, sticky="w")
        self.tile_lbl = ttk.Label(mid, text="Current tile: -")
        self.tile_lbl.grid(row=0, column=1, sticky="w", padx=12)
        self.roll_btn = ttk.Button(mid, text="Roll (Player 1)", command=self.roll_action, state='disabled')
        self.roll_btn.grid(row=0, column=2, padx=8)

        # Bottom: two logs side-by-side (Player1 | Player2/Computer)
        bottom = ttk.Frame(main)
        bottom.grid(row=2, column=0, sticky="nsew", pady=(8,0))
        # player1 log
        left_frame = ttk.Frame(bottom)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        ttk.Label(left_frame, text="Player 1 Log").grid(row=0, column=0, sticky="w")
        self.p1_log = scrolledtext.ScrolledText(left_frame, width=60, height=20, state='disabled', wrap='word')
        self.p1_log.grid(row=1, column=0, pady=6)
        # player2/computer log
        right_frame = ttk.Frame(bottom)
        right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_label = ttk.Label(right_frame, text="Computer Log")
        self.right_label.grid(row=0, column=0, sticky="w")
        self.p2_log = scrolledtext.ScrolledText(right_frame, width=40, height=20, state='disabled', wrap='word')
        self.p2_log.grid(row=1, column=0, pady=6)

        # winner label
        self.winner_lbl = ttk.Label(main, text="", font=('Segoe UI', 11, 'bold'))
        self.winner_lbl.grid(row=3, column=0, sticky="w", pady=(6,0))

        # layout config
        self.root.columnconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=2)

        # initialize UI state
        self._on_mode_change()

    # ---------- UI helpers ----------
    def _append_p1(self, text):
        self.p1_log.configure(state='normal')
        self.p1_log.insert('1.0', text + "\n")
        self.p1_log.configure(state='disabled')

    def _append_p2(self, text):
        self.p2_log.configure(state='normal')
        self.p2_log.insert('1.0', text + "\n")
        self.p2_log.configure(state='disabled')

    def _clear_logs(self):
        self.p1_log.configure(state='normal'); self.p1_log.delete('1.0','end'); self.p1_log.configure(state='disabled')
        self.p2_log.configure(state='normal'); self.p2_log.delete('1.0','end'); self.p2_log.configure(state='disabled')

    def _refresh_ui(self):
        self.status_lbl.config(text=f"Positions — P1: {self.game.p1_pos} | P2/Comp: {self.game.p2_pos}")
        self.tile_lbl.config(text="Current tile: -")
        self.winner_lbl.config(text="")
        # update roll button label based on turn and mode
        if self.mode.get() == 1:
            self.roll_btn.config(text="Roll (Player 1)" if self.current_turn == 'p1' else "Roll (Computer)")
        else:
            self.roll_btn.config(text="Roll (Player 1)" if self.current_turn == 'p1' else "Roll (Player 2)")

    # ---------- info dialogs ----------
    def show_challenges_info(self):
        info = (
            "Five Challenge Types (short):\n\n"
            "1) Number Choice — pick 1–10. Tile has hidden 'bad' numbers. If you pick a bad number you move BACK by that amount; else you move FORWARD by that amount.\n\n"
            "2) Quiz — general knowledge Q. Correct: +5 steps. Wrong: -3 steps.\n\n"
            "3) Route (Path-change) — exactly one per path. If you accept, you switch to another path but stay at same step index.\n\n"
            "4) Gamble Chest — pick 1–5. If it matches the hidden treasure you gain (num * multiplier). Else you lose that many steps.\n\n"
            "5) Puzzle (Multiplication) — a×b question. Correct: +4. Wrong: -2.\n\n"
            "First to reach 20 steps on their path wins. Player1 goes first."
        )
        messagebox.showinfo("Challenges Info", info)

    def show_path_info(self):
        lines = []
        for i, path in enumerate(self.game.paths, start=1):
            counts = {}
            for t in path.tiles:
                counts[t.type] = counts.get(t.type, 0) + 1
            lines.append(f"Path {i}: choice {counts.get('choice',0)}, quiz {counts.get('quiz',0)}, gamble {counts.get('gamble',0)}, puzzle {counts.get('puzzle',0)}, route {counts.get('route',0)}")
        messagebox.showinfo("Paths Summary", "\n".join(lines))

    # ---------- start/reset ----------
    def _on_mode_change(self):
        # toggle the visibility/label for second path selection and right log header
        if self.mode.get() == 1:
            # vs computer
            self.right_label.config(text="Computer Log")
            # default second path combo to a different path
            # keep p2 combo enabled so user can pick or leave
            self.p2_path_combo.set(str((int(self.p1_path_var.get()) % NUM_PATHS) + 1))
            self.p2_path_combo.config(state='readonly')
        else:
            # two-player
            self.right_label.config(text="Player 2 Log")
            self.p2_path_combo.config(state='readonly')
        self._refresh_ui()

    def start_game(self):
        try:
            p1 = int(self.p1_path_var.get()) - 1
        except:
            messagebox.showinfo("Select Path", "Choose player1 path (1-5).")
            return
    
        # set player1 path
        self.game.p1_path = p1
    
        if self.mode.get() == 1:
            # vs computer: auto-choose computer path (different from p1 if possible)
            choices = list(range(NUM_PATHS))
            if len(choices) > 1:
                if p1 in choices:
                    choices.remove(p1)
            p2 = random.choice(choices)
            # reflect selection in UI and lock it
            self.p2_path_var.set(str(p2+1))
            self.p2_path_combo.config(state='disabled')
            self._append_p1(f"Player1 chose Path {p1+1}.")
            self._append_p2(f"Computer chosen Path {p2+1}.")
            self.game.p2_path = p2
        else:
            # two-player: read p2 selection
            try:
                p2 = int(self.p2_path_var.get()) - 1
            except:
                messagebox.showinfo("Select Path", "Choose player2 path (1-5).")
                return
            self.game.p2_path = p2
            self._append_p1(f"Player1 chose Path {p1+1}.")
            self._append_p2(f"Player2 chose Path {p2+1}.")
            # keep p2 combo locked for consistency
            self.p2_path_combo.config(state='disabled')
    
        # lock player1 combo and enable roll button
        self.p1_path_combo.config(state='disabled')
        self.roll_btn.config(state='normal')
        self.current_turn = 'p1'
        self._refresh_ui()

    def reset_game(self):
        if not messagebox.askyesno("Reset", "Reset game and regenerate paths?"):
            return
        self.game = LuckLadder()
        self.p1_path_combo.config(state='readonly')
        self.p2_path_combo.config(state='readonly')
        self._clear_logs()
        self._refresh_ui()
        self._append_p1("Game reset. Choose paths and Start.")
        self._append_p2("Game reset.")

    # ---------- turn action ----------
    def roll_action(self):
        if self.current_turn == 'p1':
            self._player1_turn()
        else:
            if self.mode.get() == 1:
                # computer turn
                self._computer_turn()
            else:
                # player2 human turn
                self._player2_turn()

    # ---------- player1 logic ----------
    def _player1_turn(self):
        self.roll_btn.config(state='disabled')
        if self.game.p1_path is None:
            messagebox.showinfo("Start", "Choose paths and Start first.")
            return
        if self.winner_lbl.cget("text"):
            messagebox.showinfo("Game over", "Match finished. Reset to play again.")
            return
        d = self.game.roll()
        self._append_p1(f"Roll: {d}")
        self.game.p1_pos += d
        if self.game.p1_pos >= PATH_LENGTH:
            self._append_p1("Player1 reached destination!")
            self._end_and_show_winner('player1')
            return
        idx = min(PATH_LENGTH - 1, max(0, self.game.p1_pos - 1))
        tile = self.game.paths[self.game.p1_path].tiles[idx]
        self.tile_lbl.config(text=f"Current tile: {tile.describe_short()} (step {idx+1})")
        self._append_p1(f"Landed on tile {idx+1}: {tile.type.upper()}")
        self._resolve_tile_for_human(player=1, tile=tile, tile_idx=idx)
        self._refresh_ui()
        w = self.game.winner()
        if w:
            self._end_and_show_winner(w)
            return
        if self.mode.get() == 1:
            # in vs-computer mode, automatically run computer turn after a short delay
            self._refresh_ui()
            self.root.after(500, self._computer_turn)
        else:
            # two-player mode: switch to player 2 and wait for their button press
            self.current_turn = 'p2'
            self._refresh_ui()
    # ---------- player2 logic (human) ----------

    def _player2_turn(self):
        if self.game.p2_path is None:
            messagebox.showinfo("Start", "Choose paths and Start first.")
            return
        if self.winner_lbl.cget("text"):
            return
        d = self.game.roll()
        self._append_p2(f"Roll: {d}")
        self.game.p2_pos += d
        if self.game.p2_pos >= PATH_LENGTH:
            self._append_p2("Player2 reached destination!")
            self._end_and_show_winner('player2')
            return
        idx = min(PATH_LENGTH - 1, max(0, self.game.p2_pos - 1))
        tile = self.game.paths[self.game.p2_path].tiles[idx]
        self.tile_lbl.config(text=f"Current tile: {tile.describe_short()} (step {idx+1})")
        self._append_p2(f"Landed on tile {idx+1}: {tile.type.upper()}")
        self._resolve_tile_for_human(player=2, tile=tile, tile_idx=idx)
        self._refresh_ui()
        w = self.game.winner()
        if w:
            self._end_and_show_winner(w)
            return
        # switch back to player1
        self.current_turn = 'p1'
        self._refresh_ui()

    # ---------- computer logic ----------
    def _computer_turn(self):
        if self.game.p2_path is None:
            return
        if self.winner_lbl.cget("text"):
            return
        d = self.game.roll()
        self._append_p2(f"Roll: {d}")
        self.game.p2_pos += d
        if self.game.p2_pos >= PATH_LENGTH:
            self._append_p2("Computer reached destination!")
            self._end_and_show_winner('player2')
            return
        idx = min(PATH_LENGTH - 1, max(0, self.game.p2_pos - 1))
        tile = self.game.paths[self.game.p2_path].tiles[idx]
        self._append_p2(f"Landed on tile {idx+1}: {tile.type.upper()}")
        # explicit computer choices visible in log
        if tile.type == 'choice':
            pick = random.randint(1,10)
            self._append_p2(f"Computer picks {pick} (bad set: {sorted(list(tile.bad_numbers))})")
            if pick in tile.bad_numbers:
                self.game.p2_pos = max(0, self.game.p2_pos - pick)
                self._append_p2(f"Bad -> -{pick} -> {self.game.p2_pos}")
            else:
                self.game.p2_pos += pick
                self._append_p2(f"Good -> +{pick} -> {self.game.p2_pos}")
        elif tile.type == 'quiz':
            ok = random.random() < COMP_QUIZ_PROB
            self._append_p2(f"Computer quiz attempt: {'correct' if ok else 'wrong'}")
            if ok:
                self.game.p2_pos += QUIZ_FORWARD
                self._append_p2(f"+{QUIZ_FORWARD} -> {self.game.p2_pos}")
            else:
                self.game.p2_pos = max(0, self.game.p2_pos - QUIZ_BACK)
                self._append_p2(f"-{QUIZ_BACK} -> {self.game.p2_pos}")
        elif tile.type == 'route':
            do_switch = random.random() < COMP_ROUTE_ACCEPT_PROB
            if do_switch:
                choices = [i for i in range(NUM_PATHS) if i != self.game.p2_path]
                newp = random.choice(choices)
                self.game.p2_path = newp
                self._append_p2(f"Computer switched to Path {newp+1}.")
            else:
                self._append_p2("Computer stayed on path.")
        elif tile.type == 'gamble':
            pick = random.randint(1,5)
            treasure = random.randint(1,5)
            self._append_p2(f"Computer gambles {pick}; treasure {treasure}")
            if pick == treasure:
                gain = pick * GAMBLE_MULTIPLIER
                self.game.p2_pos += gain
                self._append_p2(f"Jackpot +{gain} -> {self.game.p2_pos}")
            else:
                self.game.p2_pos = max(0, self.game.p2_pos - pick)
                self._append_p2(f"Lost -{pick} -> {self.game.p2_pos}")
        elif tile.type == 'puzzle':
            a = random.randint(2,9); b = random.randint(2,9)
            ok = random.random() < COMP_PUZZLE_PROB
            self._append_p2(f"Computer puzzle {a}×{b} -> {'correct' if ok else 'wrong'}")
            if ok:
                self.game.p2_pos += PUZZLE_FORWARD
                self._append_p2(f"+{PUZZLE_FORWARD} -> {self.game.p2_pos}")
            else:
                self.game.p2_pos = max(0, self.game.p2_pos - PUZZLE_BACK)
                self._append_p2(f"-{PUZZLE_BACK} -> {self.game.p2_pos}")
        # after computer turn, back to p1
        # enable roll again for player1 (if game not finished)
        if not self.winner_lbl.cget("text"):
            self.roll_btn.config(state='normal')

        self._refresh_ui()
        self.current_turn = 'p1'
        self._refresh_ui()
        w = self.game.winner()
        if w:
            self._end_and_show_winner(w)

    # ---------- tile resolution for humans (player 1 or 2) ----------
    def _resolve_tile_for_human(self, player, tile, tile_idx):
        # player: 1 or 2
        def append(player_id, text):
            if player_id == 1:
                self._append_p1(text)
            else:
                self._append_p2(text)

        if tile.type == 'choice':
            bad = sorted(list(tile.bad_numbers))
            while True:
                ans = simpledialog.askstring("Number Choice", f"Bad numbers here: {bad}\nChoose a number 1–10:")
                if ans is None:
                    messagebox.showinfo("Required", "Please choose a number to continue.")
                    continue
                if ans.isdigit() and 1 <= int(ans) <= 10:
                    pick = int(ans); break
                messagebox.showinfo("Invalid", "Enter 1–10.")
            if player == 1:
                if pick in tile.bad_numbers:
                    self.game.p1_pos = max(0, self.game.p1_pos - pick)
                    append(1, f"You chose {pick} — BAD. Move back {pick} -> {self.game.p1_pos}")
                else:
                    self.game.p1_pos += pick
                    append(1, f"You chose {pick} — GOOD. Move forward {pick} -> {self.game.p1_pos}")
            else:
                if pick in tile.bad_numbers:
                    self.game.p2_pos = max(0, self.game.p2_pos - pick)
                    append(2, f"You chose {pick} — BAD. Move back {pick} -> {self.game.p2_pos}")
                else:
                    self.game.p2_pos += pick
                    append(2, f"You chose {pick} — GOOD. Move forward {pick} -> {self.game.p2_pos}")

        elif tile.type == 'quiz':
            q, a = tile.quiz
            ans = simpledialog.askstring("Quiz", q)
            if ans is None:
                messagebox.showinfo("Required", "Please answer the quiz.")
                return self._resolve_tile_for_human(player, tile, tile_idx)
            correct = ans.strip().lower() == a.strip().lower()
            if player == 1:
                if correct:
                    self.game.p1_pos += QUIZ_FORWARD
                    append(1, f"Quiz correct! +{QUIZ_FORWARD} -> {self.game.p1_pos}")
                else:
                    self.game.p1_pos = max(0, self.game.p1_pos - QUIZ_BACK)
                    append(1, f"Quiz wrong. Answer: {a}. -{QUIZ_BACK} -> {self.game.p1_pos}")
            else:
                if correct:
                    self.game.p2_pos += QUIZ_FORWARD
                    append(2, f"Quiz correct! +{QUIZ_FORWARD} -> {self.game.p2_pos}")
                else:
                    self.game.p2_pos = max(0, self.game.p2_pos - QUIZ_BACK)
                    append(2, f"Quiz wrong. Answer: {a}. -{QUIZ_BACK} -> {self.game.p2_pos}")

        elif tile.type == 'route':
            do_switch = messagebox.askyesno("Route", "Switch to another path at same step index?")
            if do_switch:
                choices = [i for i in range(NUM_PATHS) if i != (self.game.p1_path if player==1 else self.game.p2_path)]
                pick = simpledialog.askinteger("Switch Path", f"Available: {[c+1 for c in choices]}\nEnter path number:")
                if pick is None or (pick-1) not in choices:
                    messagebox.showinfo("Cancelled", "Invalid or cancelled. Staying.")
                    append(player, "Stayed on same path.")
                else:
                    if player == 1:
                        self.game.p1_path = pick-1
                    else:
                        self.game.p2_path = pick-1
                    append(player, f"Switched to Path {pick}.")
            else:
                append(player, "Stayed on same path.")

        elif tile.type == 'gamble':
            while True:
                ans = simpledialog.askstring("Gamble", "Pick 1–5:")
                if ans is None:
                    messagebox.showinfo("Required", "Please pick a number.")
                    continue
                if ans.isdigit() and 1 <= int(ans) <= 5:
                    pick = int(ans); break
                messagebox.showinfo("Invalid", "Enter 1–5.")
            treasure = random.randint(1,5)
            if player == 1:
                if pick == treasure:
                    gain = pick * GAMBLE_MULTIPLIER
                    self.game.p1_pos += gain
                    append(1, f"Gamble: picked {pick}; treasure {treasure}. +{gain} -> {self.game.p1_pos}")
                else:
                    self.game.p1_pos = max(0, self.game.p1_pos - pick)
                    append(1, f"Gamble: picked {pick}; treasure {treasure}. -{pick} -> {self.game.p1_pos}")
            else:
                if pick == treasure:
                    gain = pick * GAMBLE_MULTIPLIER
                    self.game.p2_pos += gain
                    append(2, f"Gamble: picked {pick}; treasure {treasure}. +{gain} -> {self.game.p2_pos}")
                else:
                    self.game.p2_pos = max(0, self.game.p2_pos - pick)
                    append(2, f"Gamble: picked {pick}; treasure {treasure}. -{pick} -> {self.game.p2_pos}")

        elif tile.type == 'puzzle':
            a = random.randint(2,9); b = random.randint(2,9)
            ans = simpledialog.askstring("Puzzle (multiplication)", f"What is {a} × {b}?")
            if ans is None:
                messagebox.showinfo("Required", "Please answer.")
                return self._resolve_tile_for_human(player, tile, tile_idx)
            if ans.isdigit() and int(ans) == a*b:
                if player == 1:
                    self.game.p1_pos += PUZZLE_FORWARD
                    append(1, f"Puzzle correct! +{PUZZLE_FORWARD} -> {self.game.p1_pos}")
                else:
                    self.game.p2_pos += PUZZLE_FORWARD
                    append(2, f"Puzzle correct! +{PUZZLE_FORWARD} -> {self.game.p2_pos}")
            else:
                if player == 1:
                    self.game.p1_pos = max(0, self.game.p1_pos - PUZZLE_BACK)
                    append(1, f"Puzzle wrong. Correct {a*b}. -{PUZZLE_BACK} -> {self.game.p1_pos}")
                else:
                    self.game.p2_pos = max(0, self.game.p2_pos - PUZZLE_BACK)
                    append(2, f"Puzzle wrong. Correct {a*b}. -{PUZZLE_BACK} -> {self.game.p2_pos}")

    # ---------- end & winner ----------
    def _end_and_show_winner(self, who):
        if who == 'player1':
            self.winner_lbl.config(text="Player 1 wins! 🎉", foreground='green')
            self._append_p1("=== PLAYER 1 WINS ===")
            self._append_p2("=== OPPONENT LOST ===")
        elif who == 'player2':
            if self.mode.get() == 1:
                self.winner_lbl.config(text="Computer wins.", foreground='red')
                self._append_p2("=== COMPUTER WINS ===")
                self._append_p1("=== YOU LOST ===")
            else:
                self.winner_lbl.config(text="Player 2 wins!", foreground='red')
                self._append_p2("=== PLAYER 2 WINS ===")
                self._append_p1("=== YOU LOST ===")
        else:
            self.winner_lbl.config(text="It's a tie.", foreground='orange')
            self._append_p1("=== TIE ==="); self._append_p2("=== TIE ===")
        # disable roll
        self.roll_btn.config(state='disabled')

# ---------- run ----------
def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
