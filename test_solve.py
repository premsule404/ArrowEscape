import sys
import os
from shared.engine.level_parser import LevelParser
from shared.engine.solver import HintSystem
from generate_levels import levels_data

for i in range(7, 10):
    lvl = levels_data[i]
    engine, meta = LevelParser.load_from_json(lvl)
    print(f"--- Level {i+1}: {lvl['name']} ---")
    moves = []
    solver = HintSystem(engine)
    step = 0
    while len(engine.board.arrows) > 0 and step < 30:
        hint = solver.get_next_hint()
        if not hint:
            print("Stuck! Remaining arrows:")
            for aid, arr in engine.board.arrows.items():
                print(f"  {aid}: pos={arr.position}, dir={arr.direction}, can_move={engine.can_move(arr)}")
            break
        engine.tap_arrow(hint)
        moves.append(hint)
        step += 1
    if len(engine.board.arrows) == 0:
        print("SOLVED in", len(moves), "moves:", moves)
