#!/usr/bin/env python3
"""
Interactive Community Connect Four Engine for tachyon-ops GitHub Profile.
Handles community moves, Link Bot AI counter-moves, and updates README.md.
"""

import json
import os
import re
import sys

ROWS = 6
COLS = 7
EMPTY = 0
RED = 1      # Community Player (🔴)
YELLOW = 2   # Link Bot (🟡)

STATE_FILE = "connect4/game.json"
README_FILE = "README.md"
REPO = "tachyon-ops/tachyon-ops"

DISC_MAP = {
    EMPTY: "⚪",
    RED: "🔴",
    YELLOW: "🟡"
}

def load_game():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return reset_game()

def reset_game(stats=None):
    if stats is None:
        stats = {"moves": 0, "games": 0, "community_wins": 0, "link_wins": 0}
    return {
        "board": [[EMPTY for _ in range(COLS)] for _ in range(ROWS)],
        "turn": "red",
        "last_move": None,
        "status": "in_progress",
        "winner": None,
        "stats": stats
    }

def save_game(game):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(game, f, indent=2)

def can_drop(board, col):
    return 0 <= col < COLS and board[0][col] == EMPTY

def drop_disc(board, col, player):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = player
            return r, col
    return None

def check_win(board, player):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == player for i in range(4)):
                return True
    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == player for i in range(4)):
                return True
    # Positive diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == player for i in range(4)):
                return True
    # Negative diagonal
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == player for i in range(4)):
                return True
    return False

def is_board_full(board):
    return all(board[0][c] != EMPTY for c in range(COLS))

def link_bot_move(board):
    """Smart AI move for Link Bot (checks winning moves, blocks opponents, or picks central columns)."""
    # 1. Check if Bot can win in one move
    for c in range(COLS):
        if can_drop(board, c):
            temp_board = [row[:] for row in board]
            drop_disc(temp_board, c, YELLOW)
            if check_win(temp_board, YELLOW):
                return c

    # 2. Check if Community can win in one move, and block it!
    for c in range(COLS):
        if can_drop(board, c):
            temp_board = [row[:] for row in board]
            drop_disc(temp_board, c, RED)
            if check_win(temp_board, RED):
                return c

    # 3. Prefer central columns
    pref_cols = [3, 2, 4, 1, 5, 0, 6]
    for c in pref_cols:
        if can_drop(board, c):
            return c

    return None

def render_board_markdown(game):
    board = game["board"]
    status = game["status"]
    stats = game["stats"]
    last_move = game.get("last_move")

    # Column links header
    links = []
    for c in range(1, COLS + 1):
        if status == "in_progress" and can_drop(board, c - 1):
            issue_title = f"connect4|drop|red|{c}"
            issue_body = f"Click+'Submit+new+issue'+to+drop+your+disc+in+Column+{c}!+Link+Bot+will+respond+automatically."
            links.append(f"[{c}](https://github.com/{REPO}/issues/new?title={issue_title}&body={issue_body})")
        else:
            links.append(f"{c}")

    header_row = "| " + " | ".join(links) + " |"
    separator = "| " + " | ".join(["---"] * COLS) + " |"

    rows_str = []
    for r in range(ROWS):
        row_cells = [DISC_MAP[board[r][c]] for c in range(COLS)]
        rows_str.append("| " + " | ".join(row_cells) + " |")

    board_table = "\n".join([header_row, separator] + rows_str)

    reset_url = f"https://github.com/{REPO}/issues/new?title=connect4|reset&body=Click+'Submit+new+issue'+to+reset+the+game+board!"

    if status == "red_won":
        status_text = f"🏆 **Victory! Community (🔴) defeated Link Bot!** 🎉 • [**Start New Match**]({reset_url})"
    elif status == "yellow_won":
        status_text = f"⚔️ **Link Bot (🟡) won! The Hero of Time defends the realm.** • [**Rematch Link**]({reset_url})"
    elif status == "draw":
        status_text = f"🤝 **Stalemate! Board is full.** • [**Start New Match**]({reset_url})"
    else:
        last_str = ""
        if last_move:
            last_str = f"*(Last move: Col {last_move['col']} by @{last_move.get('user', 'visitor')})* "
        status_text = f"🔴 **Your turn! Click a column number above [1–7] to drop a Red disc.** {last_str}• [Reset]({reset_url})"

    content = f"""<!-- CONNECT4_START -->
<div align="center">

### 🎮 Community vs Link Bot // Connect Four

{board_table}

<br/>

{status_text}

<br/>

<p>
  <img src="https://img.shields.io/badge/Total_Moves-{stats['moves']}-00f5ff?style=flat-square&logo=gamepad" />
  <img src="https://img.shields.io/badge/Games_Played-{stats['games']}-38bdf8?style=flat-square" />
  <img src="https://img.shields.io/badge/Community_Wins-{stats['community_wins']}-ef4444?style=flat-square" />
  <img src="https://img.shields.io/badge/Link_Bot_Wins-{stats['link_wins']}-eab308?style=flat-square" />
</p>

<sub>Clicking a column opens a pre-filled GitHub Issue. Submitting it triggers a GitHub Action that plays your move and Link Bot's counter-move in ~15 seconds.</sub>

</div>
<!-- CONNECT4_END -->"""
    return content

def update_readme(game):
    if not os.path.exists(README_FILE):
        return
    with open(README_FILE, "r") as f:
        readme = f.read()

    new_section = render_board_markdown(game)
    pattern = re.compile(r"<!-- CONNECT4_START -->.*?<!-- CONNECT4_END -->", re.DOTALL)
    if pattern.search(readme):
        updated_readme = pattern.sub(new_section, readme)
    else:
        # Append before Deep Metrics or at the end
        updated_readme = readme + "\n\n" + new_section

    with open(README_FILE, "w") as f:
        f.write(updated_readme)

def main():
    issue_title = os.environ.get("EVENT_ISSUE_TITLE", "").strip()
    user_login = os.environ.get("EVENT_USER_LOGIN", "challenger").strip()

    game = load_game()

    if "connect4|reset" in issue_title:
        stats = game.get("stats", {"moves": 0, "games": 0, "community_wins": 0, "link_wins": 0})
        stats["games"] += 1
        game = reset_game(stats)
        save_game(game)
        update_readme(game)
        print("Game reset successfully!")
        return

    # Parse move: connect4|drop|red|<col>
    match = re.search(r"connect4\|drop\|red\|(\d+)", issue_title)
    if not match:
        print(f"Ignored non-matching title: {issue_title}")
        return

    col = int(match.group(1)) - 1
    if game["status"] != "in_progress":
        print("Game already finished! Need reset.")
        return

    if not can_drop(game["board"], col):
        print(f"Column {col + 1} is full!")
        return

    # 1. Player move
    drop_disc(game["board"], col, RED)
    game["stats"]["moves"] += 1
    game["last_move"] = {"player": "red", "col": col + 1, "user": user_login}

    if check_win(game["board"], RED):
        game["status"] = "red_won"
        game["winner"] = "red"
        game["stats"]["community_wins"] += 1
        game["stats"]["games"] += 1
        save_game(game)
        update_readme(game)
        print(f"Community won!")
        return

    if is_board_full(game["board"]):
        game["status"] = "draw"
        game["stats"]["games"] += 1
        save_game(game)
        update_readme(game)
        print("Game ended in draw!")
        return

    # 2. Link Bot counter-move
    bot_col = link_bot_move(game["board"])
    if bot_col is not None:
        drop_disc(game["board"], bot_col, YELLOW)
        game["stats"]["moves"] += 1
        if check_win(game["board"], YELLOW):
            game["status"] = "yellow_won"
            game["winner"] = "yellow"
            game["stats"]["link_wins"] += 1
            game["stats"]["games"] += 1

    save_game(game)
    update_readme(game)
    print("Move processed successfully!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        game = load_game()
        save_game(game)
        update_readme(game)
        print("Initialized Connect 4 game state and README.")
    else:
        main()
