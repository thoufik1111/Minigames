# Hcricket.py
# Hand Cricket GUI (Tkinter) with Series support and right-side match results panel
import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ---------- Game logic (single match) ----------
class HandCricketGame:
    def __init__(self):
        self.reset_all()

    def reset_all(self):
        # format defaults
        self.format = 'T20'
        self.max_balls = 12
        self.max_wickets = 1

        # match state
        self.toss_winner = None
        self._comp_pick = None
        self.batting_first = None
        self.innings = 1  # 1 or 2
        self.current_batting = None  # 'player' or 'computer'

        # innings counters (for current innings)
        self.runs = 0
        self.wickets = 0
        self.balls = 0
        self.target = None
        self.logs = []

        # stored innings results for the match (filled when innings end)
        self.first_innings = None
        self.second_innings = None

    def set_format(self, fmt):
        fmt = fmt.upper()
        self.format = fmt
        if fmt == 'T20':
            self.max_balls = 12
            self.max_wickets = 1
        elif fmt == 'ODI':
            self.max_balls = 30
            self.max_wickets = 3
        else:
            # TEST
            self.max_balls = None
            self.max_wickets = 10

    def append_log(self, text):
        self.logs.append(text)

    def do_toss(self, call):
        coin = random.choice(['heads', 'tails'])
        if call.lower() not in ('heads','tails'):
            raise ValueError("Invalid toss call")
        if call.lower() == coin:
            self.toss_winner = 'player'
            self.append_log(f"Toss: coin={coin} -> Player won toss")
            return {'coin': coin, 'toss_winner': 'player'}
        else:
            self.toss_winner = 'computer'
            comp_pick = random.choice(['bat','bowl'])
            self._comp_pick = comp_pick
            self.append_log(f"Toss: coin={coin} -> Computer won toss and chose {comp_pick}")
            return {'coin': coin, 'toss_winner': 'computer', 'computer_choice': comp_pick}

    def choose_bat_bowl(self, choice=None, accept_computer=False):
        if self.toss_winner == 'player':
            if choice not in ('bat','bowl'):
                raise ValueError("Choice must be 'bat' or 'bowl'")
            self.batting_first = 'player' if choice == 'bat' else 'computer'
        else:
            if not accept_computer:
                raise RuntimeError("Computer pick awaiting acceptance")
            comp_pick = getattr(self, '_comp_pick', 'bat')
            self.batting_first = 'computer' if comp_pick == 'bat' else 'player'

        # start first innings
        self.innings = 1
        self.current_batting = self.batting_first
        self.runs = 0; self.wickets = 0; self.balls = 0; self.logs = []
        self.first_innings = None; self.second_innings = None
        self.append_log(f"Innings start: {self.current_batting} batting first")
        return self.batting_first

    def play_ball(self, player_num=None):
        if player_num is not None:
            if not isinstance(player_num, int) or not (1 <= player_num <= 6):
                raise ValueError("player_num must be int 1-6 or None")
        if self.max_balls is not None and self.balls >= self.max_balls:
            raise RuntimeError("No balls left; innings finished")
        if self.wickets >= self.max_wickets:
            raise RuntimeError("All wickets down; innings finished")

        is_player_batting = (self.current_batting == 'player')
        comp_num = random.randint(1,6)
        if player_num is None:
            player_num = random.randint(1,6)

        self.balls += 1
        event = ''
        innings_over = False

        if is_player_batting:
            event = f"Ball {self.balls}: Player {player_num} vs Computer {comp_num}"
            if player_num == comp_num:
                self.wickets += 1
                event += f" -> WICKET! ({self.runs}/{self.wickets})"
            else:
                self.runs += player_num
                event += f" -> Player scored {player_num}. Score: {self.runs}/{self.wickets}"
        else:
            event = f"Ball {self.balls}: Computer {comp_num} vs Player {player_num}"
            if comp_num == player_num:
                self.wickets += 1
                event += f" -> WICKET! ({self.runs}/{self.wickets})"
            else:
                self.runs += comp_num
                event += f" -> Computer scored {comp_num}. Score: {self.runs}/{self.wickets}"

        self.append_log(event)

        # check end conditions
        if self.innings == 1:
            if (self.max_balls is not None and self.balls >= self.max_balls) or self.wickets >= self.max_wickets:
                self.first_innings = {'runs': self.runs, 'wickets': self.wickets, 'balls': self.balls}
                self.target = self.runs + 1
                self.innings = 2
                self.current_batting = 'computer' if self.batting_first == 'player' else 'player'
                self.runs = 0; self.wickets = 0; self.balls = 0
                self.append_log('--- First innings ended. Second innings start ---')
                innings_over = True
        else:
            # chasing
            if self.target is not None and self.runs >= self.target:
                self.second_innings = {'runs': self.runs, 'wickets': self.wickets, 'balls': self.balls}
                innings_over = True
                self.append_log('Target reached!')
            elif (self.max_balls is not None and self.balls >= self.max_balls) or self.wickets >= self.max_wickets:
                self.second_innings = {'runs': self.runs, 'wickets': self.wickets, 'balls': self.balls}
                innings_over = True

        return {'event': event, 'runs': self.runs, 'wickets': self.wickets, 'balls': self.balls, 'innings_over': innings_over, 'target': self.target}

    def end_innings_early(self):
        if self.innings == 1:
            self.first_innings = {'runs': self.runs, 'wickets': self.wickets, 'balls': self.balls}
            self.target = self.runs + 1
            self.innings = 2
            self.current_batting = 'computer' if self.batting_first == 'player' else 'player'
            self.runs = 0; self.wickets = 0; self.balls = 0
            self.append_log('--- First innings ended early. Second innings start ---')
            return {'switched': True, 'target': self.target}
        else:
            self.second_innings = {'runs': self.runs, 'wickets': self.wickets, 'balls': self.balls}
            self.append_log('--- Match ended early by user ---')
            return {'match_over': True}

    def match_winner(self):
        # returns 'player', 'computer', or 'tie' based on the match results (both innings present)
        if not (self.first_innings and self.second_innings):
            return None
        f = self.first_innings; s = self.second_innings
        if s['runs'] > f['runs']:
            second_is_player = (self.batting_first != 'player')
            return 'player' if second_is_player else 'computer'
        elif s['runs'] < f['runs']:
            return 'player' if self.batting_first == 'player' else 'computer'
        else:
            return 'tie'

    def compute_result_text(self):
        if not (self.first_innings and self.second_innings):
            return "Match incomplete"
        f = self.first_innings; s = self.second_innings
        player_batted_first = (self.batting_first == 'player')
        if player_batted_first:
            if s['runs'] > f['runs']:
                wickets_allowed = self.max_wickets
                wickets_remaining = max(0, wickets_allowed - s['wickets'])
                return f"You lost. Computer won by {wickets_remaining} wicket(s)."
            elif s['runs'] < f['runs']:
                diff = f['runs'] - s['runs']
                return f"Congratulations! You won by {diff} run(s)."
            else:
                return f"It's a tie! Both scored {f['runs']} runs."
        else:
            if s['runs'] > f['runs']:
                wickets_allowed = self.max_wickets
                wickets_remaining = max(0, wickets_allowed - s['wickets'])
                return f"Congratulations! You won by {wickets_remaining} wicket(s)."
            elif s['runs'] < f['runs']:
                diff = f['runs'] - s['runs']
                return f"You lost. Computer won by {diff} run(s)."
            else:
                return f"It's a tie! Both scored {f['runs']} runs."

# ---------- GUI with Series support ----------
class HandCricketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Cricket — Player vs Computer (Series)")
        self.game = HandCricketGame()

        # series state
        self.series_total_games = 1
        self.series_played = 0
        self.series_player_wins = 0
        self.series_computer_wins = 0
        self.series_player_runs = 0
        self.series_computer_runs = 0
        self.series_active = False

        self.build_ui()
        self.refresh_ui()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky="nsew")

        # Top row: format, rules, series, toss
        top = ttk.Frame(frm)
        top.grid(row=0, column=0, sticky="w", pady=4)

        ttk.Label(top, text="Format:").grid(row=0,column=0, sticky="w")
        self.fmt_var = tk.StringVar(value="T20")
        fmt_combo = ttk.Combobox(top, textvariable=self.fmt_var, values=["T20","ODI","TEST"], state="readonly", width=6)
        fmt_combo.grid(row=0,column=1, padx=6)
        fmt_combo.bind("<<ComboboxSelected>>", lambda e: self.on_format_change())

        # Format rules label (separate box)
        self.rule_lbl = ttk.Label(top, text="", foreground='blue', font=('Segoe UI', 10, 'bold'))
        self.rule_lbl.grid(row=1, column=0, columnspan=8, sticky="w", pady=(4,0))

        # Series selection (only for T20 and ODI)
        ttk.Label(top, text="Series:").grid(row=0, column=2, sticky="w")
        self.series_var = tk.StringVar(value="1")
        self.series_combo = ttk.Combobox(top, textvariable=self.series_var, values=["1","3","5","7"], state="readonly", width=4)
        self.series_combo.grid(row=0, column=3, sticky="w", padx=(4,0))

        ttk.Label(top, text="Toss:").grid(row=0,column=4, padx=(12,0))
        self.toss_call = tk.StringVar(value="heads")
        ttk.Combobox(top, textvariable=self.toss_call, values=["heads","tails"], state="readonly", width=6).grid(row=0,column=5, padx=6)

        self.toss_btn = ttk.Button(top, text="Play Toss", command=self.do_toss)
        self.toss_btn.grid(row=0,column=6, padx=(8,0))

        self.toss_info = ttk.Label(top, text="", foreground="orange")
        self.toss_info.grid(row=0,column=7, padx=(12,0))

        # Choice area where player accepts computer or chooses bat/bowl
        self.choose_frame = ttk.Frame(frm)
        self.choose_frame.grid(row=1, column=0, sticky="w", pady=6)

        # Score & controls
        mid = ttk.Frame(frm)
        mid.grid(row=2, column=0, sticky="nsew", pady=6)
        self.score_lbl = ttk.Label(mid, text="Score: 0/0", font=('Segoe UI', 14, 'bold'))
        self.score_lbl.grid(row=0,column=0, sticky="w")
        self.balls_lbl = ttk.Label(mid, text="Balls: 0")
        self.balls_lbl.grid(row=0,column=1, padx=12)
        self.target_lbl = ttk.Label(mid, text="Target: -")
        self.target_lbl.grid(row=0,column=2, padx=12)

        controls = ttk.Frame(mid)
        controls.grid(row=1, column=0, columnspan=3, sticky="w", pady=8)
        ttk.Label(controls, text="Enter number (1-6):").grid(row=0,column=0, sticky="w")
        self.num_entry = ttk.Entry(controls, width=4)
        self.num_entry.grid(row=0,column=1, padx=6)
        self.play_btn = ttk.Button(controls, text="Play Ball", command=self.play_ball_clicked)
        self.play_btn.grid(row=0,column=2, padx=6)
        self.auto_btn = ttk.Button(controls, text="Auto Ball", command=self.auto_ball)
        self.auto_btn.grid(row=0,column=3, padx=6)
        self.end_btn = ttk.Button(controls, text="End Innings", command=self.end_innings)
        self.end_btn.grid(row=0,column=4, padx=6)

        # Log area and Series results area side-by-side
        logframe = ttk.Frame(frm)
        logframe.grid(row=3, column=0, sticky="nsew")
        # left: ball-by-ball log
        left_frame = ttk.Frame(logframe)
        left_frame.grid(row=0, column=0, sticky="nsew")
        ttk.Label(left_frame, text="Ball-by-ball Log:").grid(row=0,column=0, sticky="w")
        self.log_box = scrolledtext.ScrolledText(left_frame, width=60, height=16, state='disabled', wrap='word', background='#081526', foreground='white')
        self.log_box.grid(row=1,column=0, pady=6)

        # right: series match results
        right_frame = ttk.Frame(logframe)
        right_frame.grid(row=0, column=1, padx=(12,0), sticky="n")
        ttk.Label(right_frame, text="Series Match Results:").grid(row=0,column=0, sticky="w")
        self.series_results_box = scrolledtext.ScrolledText(right_frame, width=40, height=16, state='disabled', wrap='word', background='#0b2533', foreground='white')
        self.series_results_box.grid(row=1,column=0, pady=6)

        # Bottom: result and series info and next-match button
        bot = ttk.Frame(frm)
        bot.grid(row=4, column=0, sticky="w", pady=6)
        self.result_lbl = ttk.Label(bot, text="", foreground='lightgreen', font=('Segoe UI', 11, 'bold'))
        self.result_lbl.grid(row=0,column=0, sticky="w")

        # series info
        self.series_info_lbl = ttk.Label(bot, text="", foreground='lightblue')
        self.series_info_lbl.grid(row=1, column=0, sticky="w", pady=(6,0))

        self.next_match_btn = ttk.Button(bot, text="Next Match", command=self.prepare_next_match)
        self.next_match_btn.grid(row=0, column=1, padx=8)
        self.next_match_btn.state(['disabled'])

        ttk.Button(bot, text="Reset Game", command=self.reset_game).grid(row=0,column=2, padx=8)

    def on_format_change(self):
        fmt = self.fmt_var.get()
        self.game.set_format(fmt)
        # show rules
        if fmt == "T20":
            rule_text = "T20 — 2 overs (12 balls), 1 wicket max. Innings ends after 12 balls or 1 wicket."
        elif fmt == "ODI":
            rule_text = "ODI — 5 overs (30 balls), 3 wickets max. Innings ends after 30 balls or 3 wickets."
        else:
            rule_text = "TEST — No over limit, 10 wickets max. Innings ends when all 10 wickets fall."
        self.rule_lbl.config(text=rule_text)

        # series only for T20 and ODI
        if fmt == "TEST":
            self.series_combo.set("1")
            self.series_combo.state(['disabled'])
        else:
            self.series_combo.state(['!disabled'])
        self.refresh_ui()

    def do_toss(self):
        call = self.toss_call.get()
        try:
            res = self.game.do_toss(call)
        except Exception as e:
            messagebox.showinfo("Error", str(e))
            return
        if res['toss_winner'] == 'player':
            self.toss_info.config(text="You won the toss. Choose to bat or bowl.")
            for w in self.choose_frame.winfo_children(): w.destroy()
            ttk.Label(self.choose_frame, text="Choose:").grid(row=0,column=0)
            self.pick_var = tk.StringVar(value='bat')
            ttk.Radiobutton(self.choose_frame, text="Bat", variable=self.pick_var, value='bat').grid(row=0,column=1)
            ttk.Radiobutton(self.choose_frame, text="Bowl", variable=self.pick_var, value='bowl').grid(row=0,column=2)
            ttk.Button(self.choose_frame, text="Start Match", command=self.start_match_player_choice).grid(row=0,column=3, padx=6)
        else:
            comp_pick = res.get('computer_choice','bat')
            self.toss_info.config(text=f"Computer won toss and chose {comp_pick}. Click Proceed to start.")
            for w in self.choose_frame.winfo_children(): w.destroy()
            ttk.Button(self.choose_frame, text="Proceed", command=self.start_match_accept_computer).grid(row=0,column=0)

    def start_match_player_choice(self):
        choice = self.pick_var.get()
        try:
            batting_first = self.game.choose_bat_bowl(choice)
        except Exception as e:
            messagebox.showinfo("Error", str(e))
            return
        self.toss_info.config(text=f"Match started. {batting_first.capitalize()} batting first.")
        for w in self.choose_frame.winfo_children(): w.destroy()
        self.after_match_reset_ui_for_play()
        self.refresh_ui()

    def start_match_accept_computer(self):
        try:
            batting_first = self.game.choose_bat_bowl(accept_computer=True)
        except Exception as e:
            messagebox.showinfo("Error", str(e))
            return
        self.toss_info.config(text=f"Match started. {batting_first.capitalize()} batting first.")
        for w in self.choose_frame.winfo_children(): w.destroy()
        self.after_match_reset_ui_for_play()
        self.refresh_ui()

    def after_match_reset_ui_for_play(self):
        # when a match starts, make sure series settings are applied/initialized
        self.series_total_games = int(self.series_var.get())
        self.series_active = self.series_total_games > 1
        # if starting a fresh series, zero counters
        if self.series_played == 0:
            self.series_player_wins = 0
            self.series_computer_wins = 0
            self.series_player_runs = 0
            self.series_computer_runs = 0
            # clear right-side results box
            self.series_results_box.configure(state='normal')
            self.series_results_box.delete('1.0','end')
            self.series_results_box.configure(state='disabled')
        # enable controls
        for w in (self.play_btn, self.auto_btn, self.end_btn, self.num_entry):
            w.state(['!disabled'])

    def append_log(self, text):
        self.game.append_log(text)
        self.log_box.configure(state='normal')
        self.log_box.insert('1.0', text + "\n")
        self.log_box.configure(state='disabled')

    def add_series_result(self, text):
        # append a single-line match result to the right-side box
        self.series_results_box.configure(state='normal')
        self.series_results_box.insert('end', text + "\n")
        self.series_results_box.configure(state='disabled')

    def refresh_ui(self):
        # scoreboard and labels
        self.score_lbl.config(text=f"Score: {self.game.runs}/{self.game.wickets}")
        balls_text = str(self.game.balls) + (f" / {self.game.max_balls}" if self.game.max_balls is not None else "")
        self.balls_lbl.config(text=f"Balls: {balls_text}")
        self.target_lbl.config(text=f"Target: {self.game.target if self.game.target is not None else '-'}")
        # controls enabled only after innings begun
        started = self.game.current_batting is not None
        if started:
            for w in (self.play_btn, self.auto_btn, self.end_btn, self.num_entry):
                w.state(['!disabled'])
        else:
            for w in (self.play_btn, self.auto_btn, self.end_btn, self.num_entry):
                w.state(['disabled'])
        # show series info
        self.series_info_lbl.config(text=self.series_status_text())
        # if match ended show result
        if self.game.first_innings and self.game.second_innings:
            res = self.game.compute_result_text()
            self.result_lbl.config(text=res)
        else:
            self.result_lbl.config(text="")

    def play_ball_clicked(self):
        v = self.num_entry.get().strip()
        if not v or not v.isdigit() or not (1 <= int(v) <= 6):
            messagebox.showinfo("Invalid", "Enter a number 1-6")
            return
        n = int(v)
        try:
            out = self.game.play_ball(n)
        except Exception as e:
            messagebox.showinfo("Notice", str(e))
            return
        self.append_log(out['event'])
        if out['innings_over']:
            self.append_log("Innings switched/ended.")
        self.refresh_ui()
        self.num_entry.delete(0,'end')
        if self.game.first_innings and self.game.second_innings:
            self.on_match_end()

    def auto_ball(self):
        try:
            out = self.game.play_ball(None)
        except Exception as e:
            messagebox.showinfo("Notice", str(e))
            return
        self.append_log(out['event'])
        if out['innings_over']:
            self.append_log("Innings switched/ended.")
        self.refresh_ui()
        if self.game.first_innings and self.game.second_innings:
            self.on_match_end()

    def end_innings(self):
        ans = messagebox.askyesno("Confirm", "End this innings early?")
        if not ans: return
        res = self.game.end_innings_early()
        if 'switched' in res:
            self.append_log("First innings ended by user.")
            self.append_log(f"Target is {self.game.target}")
            self.refresh_ui()
        else:
            self.append_log("Match ended by user.")
            self.refresh_ui()
            self.disable_game_controls()
            if self.game.first_innings and self.game.second_innings:
                self.on_match_end()

    def on_match_end(self):
        # compute match winner and update series totals
        winner = self.game.match_winner()  # 'player'/'computer'/'tie'
        f = self.game.first_innings; s = self.game.second_innings
        if not (f and s):
            return

        if self.game.batting_first == 'player':
            player_runs_match = f['runs']
            computer_runs_match = s['runs']
        else:
            computer_runs_match = f['runs']
            player_runs_match = s['runs']

        # update series totals
        self.series_played += 1
        self.series_player_runs += player_runs_match
        self.series_computer_runs += computer_runs_match

        if winner == 'player':
            self.series_player_wins += 1
            match_text = f"Match {self.series_played}: You won (You {player_runs_match} - Computer {computer_runs_match})"
        elif winner == 'computer':
            self.series_computer_wins += 1
            match_text = f"Match {self.series_played}: Computer won (Computer {computer_runs_match} - You {player_runs_match})"
        else:
            match_text = f"Match {self.series_played}: Tie (You {player_runs_match} - Computer {computer_runs_match})"

        # log in left panel
        self.append_log("=== Match Over ===")
        self.append_log(self.game.compute_result_text())
        self.append_log(match_text)
        self.append_log(f"Series so far: You {self.series_player_wins} - Computer {self.series_computer_wins} (Runs: You {self.series_player_runs} - Comp {self.series_computer_runs})")

        # add to right-side series results panel
        self.add_series_result(match_text)

        # disable match controls until user clicks Next Match (if series continues)
        self.disable_game_controls()

        # determine if series concluded early (majority reached)
        majority = (self.series_total_games // 2) + 1
        series_winner = None
        if self.series_player_wins >= majority:
            series_winner = 'player'
        elif self.series_computer_wins >= majority:
            series_winner = 'computer'

        if self.series_played >= self.series_total_games or series_winner is not None:
            # series ended — decide winner (if tie in matches, decide by total runs)
            if self.series_player_wins > self.series_computer_wins:
                final_text = f"Series Over: You won the series {self.series_player_wins}-{self.series_computer_wins} (Total runs You {self.series_player_runs} - Comp {self.series_computer_runs})"
            elif self.series_computer_wins > self.series_player_wins:
                final_text = f"Series Over: Computer won the series {self.series_computer_wins}-{self.series_player_wins} (Total runs Comp {self.series_computer_runs} - You {self.series_player_runs})"
            else:
                # match-wins tied -> decide by runs
                if self.series_player_runs > self.series_computer_runs:
                    final_text = f"Series Over (by runs): You {self.series_player_runs} - Comp {self.series_computer_runs} -> You win the series"
                elif self.series_computer_runs > self.series_player_runs:
                    final_text = f"Series Over (by runs): Computer {self.series_computer_runs} - You {self.series_player_runs} -> Computer wins the series"
                else:
                    final_text = f"Series Over: It's an exact tie! Both won {self.series_player_wins} matches and scored {self.series_player_runs} runs."
            self.append_log(final_text)
            self.add_series_result(final_text)
            messagebox.showinfo("Series Result", final_text)
            # reset series state so user can start a new series or reset
            self.series_active = False
            self.next_match_btn.state(['disabled'])
        else:
            # series continues -> enable Next Match button so user can start next game
            self.series_total_games = int(self.series_var.get())
            self.next_match_btn.state(['!disabled'])

        self.refresh_ui()

    def series_status_text(self):
        if not self.series_active and self.series_played == 0:
            # upcoming
            if self.game.format == 'TEST':
                return "Series: Not available for TEST (single match)."
            return f"Series: Best of {self.series_var.get()} selected."
        else:
            return f"Series: Played {self.series_played}/{self.series_total_games} - You {self.series_player_wins} : Comp {self.series_computer_wins} (Runs You {self.series_player_runs} - Comp {self.series_computer_runs})"

    def prepare_next_match(self):
        # Prepare new match in the series (reset game while keeping series totals and chosen format)
        if self.series_played >= int(self.series_var.get()):
            messagebox.showinfo("Series", "All series matches already played.")
            self.next_match_btn.state(['disabled'])
            return
        # reset game state for a fresh match while preserving format
        current_fmt = self.fmt_var.get()
        self.game = HandCricketGame()
        self.game.set_format(current_fmt)
        # ensure toss/who bats will be decided again
        self.game.toss_winner = None
        self.game.batting_first = None
        # disable next-match until match ends again
        self.next_match_btn.state(['disabled'])
        # log start of next match in left panel and right panel remains as history
        self.log_box.configure(state='normal')
        self.log_box.insert('1.0', f"\n--- Starting Match {self.series_played+1} ---\n")
        self.log_box.configure(state='disabled')
        self.toss_info.config(text="Start toss for next match.")
        self.refresh_ui()

    def disable_game_controls(self):
        for w in (self.play_btn, self.auto_btn, self.end_btn, self.num_entry):
            w.state(['disabled'])

    def reset_game(self):
        ans = messagebox.askyesno("Reset", "Reset the whole game and series?")
        if not ans: return
        self.game.reset_all()
        # reset series
        self.series_total_games = 1
        self.series_played = 0
        self.series_player_wins = 0
        self.series_computer_wins = 0
        self.series_player_runs = 0
        self.series_computer_runs = 0
        self.series_active = False
        # reset UI widgets
        self.fmt_var.set("T20")
        self.series_var.set("1")
        self.toss_call.set("heads")
        self.toss_info.config(text="")
        for w in self.choose_frame.winfo_children(): w.destroy()
        self.log_box.configure(state='normal')
        self.log_box.delete('1.0','end')
        self.log_box.configure(state='disabled')
        self.series_results_box.configure(state='normal')
        self.series_results_box.delete('1.0','end')
        self.series_results_box.configure(state='disabled')
        self.next_match_btn.state(['disabled'])
        self.refresh_ui()

def main():
    root = tk.Tk()
    app = HandCricketGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
