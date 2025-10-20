# 🎮 Python Mini Games 

This repository contains three fun Python-based mini games built with **pure Python** and **Tkinter**.  
Both are playable directly GUI after we ran the code on VScode

---

# 🏏 Hand Cricket

A classic **Player vs Computer** cricket simulation game.

### 🎯 How It Works
- The match starts with a **toss** (Heads/Tails).  
- The **toss winner** chooses to **bat** or **bowl** first.
- Each side scores runs by entering numbers **1 to 6**.
- If both the player and computer choose the **same number**, the batsman is **out**.

### ⚙️ Game Formats
- **T20:** 2 overs (12 balls), 1 wicket.  
- **ODI:** 5 overs (30 balls), 3 wickets.  
- **TEST:** Unlimited balls, 10 wickets.

### 🏆 Winning Conditions
- The batting side sets a **target = total runs + 1**.  
- The chasing side must reach it before losing all wickets.  
- Final results show:
  - **Win by runs** (if batting first)
  - **Win by wickets** (if batting second)
  - **Loss by runs/wickets** (as applicable)

---

# 🎲 Luck Ladder

A creative **race-to-the-top** game built with **Tkinter GUI**, where luck and small challenges decide who reaches the goal first!

### 🎮 How It Works
- Choose mode:  
  - **1:** Player vs Computer  
  - **2:** Player vs Player  
- Select a **path (1–5)** — each path has **20 steps** and hidden tiles.
- Roll a dice to move ahead; each tile triggers one of **5 random challenges**.

### 🧩 Tile Challenges
1. **Number Choice:** Pick 1–10 — bad numbers make you move back, good ones forward.  
2. **Quiz:** Answer a quick general knowledge question (right +5, wrong -3).  
3. **Route Change:** Choose to switch to another path mid-way (can be good or bad).  
4. **Gamble Chest:** Guess a number (1–5). If it matches the hidden one, gain points, else lose.  
5. **Puzzle:** Solve a small **multiplication question** to move forward.

### 🏁 Rules
- There are **5 paths**, each with **20 steps**.
- First to reach **step 20** wins.  
- Computer makes automatic moves in single-player mode.
- Includes **Reset**, **Challenges Info**, and **Path Info** buttons.

---
# 🔪 Hide & Kill

A tense, multi-player deduction game where players must choose the best room to hide in before the Killer strikes!

### 🎯 How It Works

The game is played over **10 rounds** on a fixed, 8-room house layout.

1. **Hiding Phase:** Each player simultaneously selects a room number (1 to 8) to hide in.

2. **Killer Phase:** The game randomly determines a single **Safe Room** (the room the Killer overlooks).

3. **Search Animation:** The Killer visibly moves through the other **7 rooms** one by one, checking them sequentially.

4. Any player hiding in a room that the Killer searches is **caught**.

5. The **Safe Room** is revealed in **Green** at the end of the search sequence.

### ⚙️ Rules & Mechanics

| Feature | Detail | 
 | ----- | ----- | 
| **Player Count** | Minimum **2** players, maximum **6** players. | 
| **Scoring** | All players start with **10 points**. | 
| **Loss Condition** | If your chosen room is searched (it turns **Red**), you lose **1 point**. | 
| **Round Goal** | Choose the one room that the Killer does **not** search (the **Safe Room**). | 
| **Layout** | The game uses a **fixed 8-room interior layout** to simulate a real house. | 
| **Tension** | The Killer's path is **animated**, searching 7 rooms sequentially before revealing the result. | 

### 🏆 Winning Conditions

* The game consists of **10 total rounds**.

* At the end of the 10th round, all final scores are tallied.

* The player with the **highest remaining point total** is declared the winner!
  
---

## 💡 Requirements
- Python 3.8+
- Tkinter (comes pre-installed with most Python versions)

---

