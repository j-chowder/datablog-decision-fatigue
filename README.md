# datablog-decision-fatigue

## move_level_data.csv variables

| Column               | Type      | Description                                                                                                         |
| -------------------- | --------- | ------------------------------------------------------------------------------------------------------------------- |
| `move_number`        | int       | Global move index within the game (increments every move, includes both players).                                   |
| `player_move_number` | int       | Move index per player (counts only that player’s decisions).                                                        |
| `move`               | string    | Move in Standard Algebraic Notation (SAN), e.g., `Nf3`, `e4`.                                                       |
| `cpl`                | float     | Centipawn Loss — difference between the best engine move and the played move; measures decision quality.            |
| `difficulty`         | float     | Absolute difference between the top two engine move evaluations; higher values indicate more unforgiving positions. |
| `is_blunder`         | int (0/1) | Indicator for major mistakes; `1` if `cpl > 100`, otherwise `0`.  
