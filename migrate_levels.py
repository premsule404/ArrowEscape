import os, json

print("--- MIGRATING LEVEL DATA TO REMOVE DEPRECATED MOVE-BASED STAR THRESHOLDS ---")
for i in range(1, 21):
    path = f"levels/level{i:03d}.json"
    if not os.path.exists(path): continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rewards = data.get("rewards", {})
    if "stars_thresholds" in rewards:
        del rewards["stars_thresholds"]
    data["rewards"] = rewards
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

print("ALL 20 LEVEL JSON FILES MIGRATED CLEANLY!")
