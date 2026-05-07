import chess
import chess.engine
import pandas as pd
import numpy as np
import os


# ----------------------------
# CONFIG
# ----------------------------
STOCKFISH_PATH = "stockfish-windows-x86-64-avx2.exe"   # update if needed
DEPTH = 12                     # increase later if needed

engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
df = pd.read_csv('./data/raw/data.csv')
start_idx = df.index[df['id'] == '8c3usY4b'][0]
df = df.loc[start_idx:] 

# ----------------------------
# SAFE SCORE
# ----------------------------
def safe_score(score):
    # Convert mate scores to large centipawn values
    if score.is_mate():
        return 10000 if score.mate() > 0 else -10000
    return score.score()

# ----------------------------
# CORE FUNCTION (ONE GAME)
# ----------------------------
def evaluate_game(game_id, moves_str, white_id, black_id, depth=DEPTH, cache=None):
    board = chess.Board()
    moves = moves_str.split()

    rows = []

    for i, move in enumerate(moves):
        move_number = i + 1

        # Determine player + color
        if move_number % 2 == 1:
            player_id = white_id
            color = "white"
        else:
            player_id = black_id
            color = "black"

        # Per-player move index
        player_move_number = (move_number + 1) // 2

        fen_before = board.fen()
        turn = board.turn  # ✅ CRITICAL FIX: perspective

        # ----------------------------
        # GET BEST + SECOND BEST (CACHE)
        # ----------------------------
        if cache is not None and fen_before in cache:
            best_eval, second_eval = cache[fen_before]
        else:
            try:
                info = engine.analyse(
                    board,
                    chess.engine.Limit(depth=depth),
                    multipv=2
                )

                best_eval = safe_score(info[0]["score"].pov(turn))
                second_eval = safe_score(info[1]["score"].pov(turn))

                if cache is not None:
                    cache[fen_before] = (best_eval, second_eval)

            except:
                continue  # skip if engine fails

        # ----------------------------
        # PLAY MOVE
        # ----------------------------
        try:
            board.push_san(move)
        except:
            continue  # skip invalid moves

        # ----------------------------
        # EVALUATE AFTER MOVE
        # ----------------------------
        try:
            info_after = engine.analyse(
                board,
                chess.engine.Limit(depth=depth)
            )
            played_eval = safe_score(info_after["score"].pov(turn))
        except:
            continue

        # ----------------------------
        # METRICS
        # ----------------------------
        cpl_raw = best_eval - played_eval
        cpl = max(0, cpl_raw)  # ✅ ensure non-negative

        # Optional: cap extreme noise (recommended)
        cpl = min(cpl, 1000)

        difficulty = best_eval - second_eval  # ✅ already ordered
        difficulty = min(difficulty, 1000)

        is_blunder = int(cpl > 100)

        rows.append({
            "game_id": game_id,
            "player_id": player_id,
            "color": color,
            "move_number": move_number,
            "player_move_number": player_move_number,
            "move": move,
            "cpl": cpl,
            "difficulty": difficulty,
            "is_blunder": is_blunder
        })

    return rows

# ----------------------------
# MAIN PIPELINE (ALL GAMES)
# ----------------------------
def evaluate_dataframe(df, output_file="./data/processed/move_level_data_v2.csv"):
    cache = {}

    write_header = not os.path.exists(output_file)

    for idx, row in df.iterrows():
        result = evaluate_game(
            game_id=row["id"],
            moves_str=row["moves"],
            white_id=row["white_id"],
            black_id=row["black_id"],
            cache=cache
        )

        if not result:
            continue

        temp_df = pd.DataFrame(result)

        temp_df.to_csv(
            output_file,
            mode="a",
            header=write_header,
            index=False
        )

        write_header = False

        if idx % 100 == 0:
            print(f"Processed {idx} games")

    print("Done.")

evaluate_dataframe(df)