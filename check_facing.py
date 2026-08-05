import os, json

print("--- CHECKING FOR HEAD-ON FACING ARROWS ---")
for i in range(1, 21):
    path = f"levels/level{i:03d}.json"
    if not os.path.exists(path): continue
    with open(path) as f:
        data = json.load(f)
    arrows = data.get("arrows", [])
    facing_found = False
    for a1 in arrows:
        for a2 in arrows:
            if a1["id"] >= a2["id"]: continue
            x1, y1, d1 = a1["x"], a1["y"], a1["direction"]
            x2, y2, d2 = a2["x"], a2["y"], a2["direction"]
            # Same row facing head-on
            if y1 == y2:
                if x1 < x2 and d1 == "RIGHT" and d2 == "LEFT":
                    # Check if any arrow is between them
                    between = [a for a in arrows if a["y"] == y1 and x1 < a["x"] < x2]
                    if not between:
                        print(f"[{path}] HEAD-ON CONFLICT: Arrow {a1['id']}({x1},{y1}) RIGHT vs Arrow {a2['id']}({x2},{y2}) LEFT")
                        facing_found = True
            # Same column facing head-on
            if x1 == x2:
                if y1 < y2 and d1 == "DOWN" and d2 == "UP":
                    between = [a for a in arrows if a["x"] == x1 and y1 < a["y"] < y2]
                    if not between:
                        print(f"[{path}] HEAD-ON CONFLICT: Arrow {a1['id']}({x1},{y1}) DOWN vs Arrow {a2['id']}({x2},{y2}) UP")
                        facing_found = True

if not facing_found:
    print("NO HEAD-ON FACING ARROWS FOUND IN ANY LEVEL!")
